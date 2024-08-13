import asyncio
import os
import logging
import time
from decimal import Decimal

from web3 import Web3
from uniswap_universal_router_decoder import FunctionRecipient, RouterCodec
import eth_abi

import sys # for testing
sys.path.append('..')

from library import Singleton
from helpers.decorators import timer_decorator, async_timer_decorator
from helpers.utils import load_contract_bin, encode_address, encode_uint, func_selector, \
                            decode_address, decode_pair_reserves, decode_int, load_router_contract, \
                            load_abi, calculate_next_block_base_fee, calculate_balance_storage_index, rpad_int, \
                            calculate_allowance_storage_index

from data import BlockData, SimulationResult, Pair
import eth_utils

class Simulator:
    @timer_decorator
    def __init__(self, 
                 http_url, 
                 signer, 
                 router_address, 
                 weth,
                 inspector,
                 pair_abi,
                 weth_abi,
                 inspector_abi,
                 ):
        logging.info(f"start simulation...")

        self.http_url = http_url
        self.signer = signer

        self.router_address = router_address
        self.weth = weth

        self.w3 = Web3(Web3.HTTPProvider(http_url))
        self.pair_abi = pair_abi
        self.weth_contract = self.w3.eth.contract(address=weth, abi=weth_abi)
        self.inspector = self.w3.eth.contract(address=inspector, abi=inspector_abi)

    @timer_decorator
    def inspect_token_by_transfer(self, token, amount):
        try:
            balance_index = calculate_balance_storage_index(self.signer,0)
            allowance_index = calculate_allowance_storage_index(self.signer, self.inspector.address,1)
            
            # result = self.w3.eth.call({
            #     'from': self.signer,
            #     'to': token,
            #     'data': bytes.fromhex(
            #         func_selector('transfer(address,uint256)') + encode_address(self.inspector.address) + encode_uint(amount)
            #     )
            # }, 'latest', {
            #     token: {
            #         'stateDiff': {
            #             balance_index.hex(): hex(amount),
            #         }
            #     }
            # })
            # logging.info(f"transfer result {Web3.to_int(result)}")

            # result = self.w3.eth.call({
            #     'from': self.signer,
            #     'to': token,
            #     'data': bytes.fromhex(
            #         func_selector('allowance(address,address)') + encode_address(self.signer) + encode_address(self.inspector.address)
            #     )
            # }, 'latest', {
            #     token: {
            #         'stateDiff': {
            #             balance_index.hex(): hex(amount),
            #             allowance_index.hex(): hex(amount),
            #         }
            #     }
            # })
            # logging.info(f"allowance result {Web3.to_int(result)}")

            result = self.w3.eth.call({
                'from': self.signer,
                'to': self.inspector.address,
                'data': bytes.fromhex(
                    func_selector('inspect_transfer(address,uint256)') + encode_address(token) + encode_uint(Web3.to_wei(amount, 'ether'))
                )
            }, 'latest', {
                token: {
                    'stateDiff': {
                        balance_index.hex(): hex(Web3.to_wei(amount, 'ether')),
                        allowance_index.hex(): hex(Web3.to_wei(amount, 'ether')),
                    }
                }
            })

            logging.info(f"inspect_transfer result {Web3.from_wei(Web3.to_int(result), 'ether')}")

            amount_out=Web3.from_wei(Web3.to_int(result), 'ether')
            slippage=(Decimal(amount_out)-Decimal(amount))/Decimal(amount)*Decimal(100)

            return (amount, amount_out, slippage, amount)
        except Exception as e:
            logging.error(f"inspect token {token} failed with error {e}")
            return None
        
    @timer_decorator
    def inspect_token_by_swap(self, token, amount):
        try:
            # result = self.w3.eth.call({
            #     'from': self.signer,
            #     'to': self.inspector.address,
            #     'value': Web3.to_wei(amount, 'ether'),
            #     'data': bytes.fromhex(
            #         func_selector('inspect(address)') + encode_address(token)
            #     )
            # }, 'latest', state_override)

            # result = eth_abi.decode(['(uint256,uint256,uint256)'], result)
            
            # slippage = (Decimal(result[0][0]) - Decimal(result[0][2]))/Decimal(result[0][0])*Decimal(10_000) # in basis points
            # slippage = round(slippage,5)

            # buy
            result = self.w3.eth.call({
                'from': self.signer,
                'to': self.inspector.address,
                'value': Web3.to_wei(amount, 'ether'),
                'data': bytes.fromhex(
                    func_selector('buy(address,uint256)') + encode_address(token) + encode_uint(int(time.time()) + 1000)
                )
            }, 'latest', {
                self.signer: {
                    'balance': hex(10**18)
                }
            })

            resultBuy = eth_abi.decode(['uint[]'], result)

            assert len(resultBuy[0]) == 2
            assert resultBuy[0][0] == Web3.to_wei(amount, 'ether')

            logging.info(f"SIMULATOR buy result {resultBuy}")

            # sell
            storage_index = calculate_balance_storage_index(self.inspector.address, 0)

            result = self.w3.eth.call({
                'from': self.signer,
                'to': self.inspector.address,
                'data': bytes.fromhex(
                    func_selector('sell(address,address,uint256)') + encode_address(token) + encode_address(self.signer) + encode_uint(int(time.time()) + 1000)
                )
            }, 'latest', {
                token: {
                    'stateDiff': {
                        storage_index.hex(): hex(resultBuy[0][1]),
                    }
                }
            })

            resultSell = eth_abi.decode(['uint[]'], result)

            assert len(resultSell[0]) == 2
            assert resultSell[0][0] == resultBuy[0][1]

            logging.info(f"SIMULATOR sell result {resultSell}")

            amount_out = Web3.from_wei(resultSell[0][1], 'ether')
            slippage = (Decimal(amount) - Decimal(amount_out))/Decimal(amount)*Decimal(10000)
            amount_token = Web3.from_wei(resultBuy[0][1], 'ether')
            
            return (amount, amount_out, slippage, amount_token)
        except Exception as e:
            logging.error(f"inspect failed with error {e}")
            return None
        
    def inspect_pair(self, pair: Pair, amount, swap=True) -> None:
        if swap is False:
            result = self.inspect_token_by_transfer(pair.token, amount)
        else:
            result = self.inspect_token_by_swap(pair.token, amount)

        if result is not None:  
            return SimulationResult(
                pair=pair,
                amount_in=result[0],
                amount_out=result[1],
                slippage=result[2],
                amount_token=result[3],
                )
        
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    PAIR_ABI = load_abi(f"{os.path.dirname(__file__)}/../contracts/abis/UniV2Pair.abi.json")
    WETH_ABI = load_abi(f"{os.path.dirname(__file__)}/../contracts/abis/WETH.abi.json")
    INSPECTOR_ABI = load_abi(f"{os.path.dirname(__file__)}/../contracts/abis/InspectBot.abi.json")

    ETH_BALANCE = 1000
    GAS_LIMIT = 200*10**3
    FEE_BPS = 25

    simulator = Simulator(os.environ.get('HTTPS_URL'),
                            os.environ.get('EXECUTION_ADDRESSES').split(',')[2],
                            os.environ.get('ROUTER_ADDRESS'),
                            os.environ.get('WETH_ADDRESS'),
                            os.environ.get('INSPECTOR_BOT').split(',')[2],
                            PAIR_ABI,
                            WETH_ABI,
                            INSPECTOR_ABI,
                            )
    
    result=simulator.inspect_pair(Pair(
        address='0x588Ca67e19926370cF091A8C1930A5AfB770e4b3',
        token='0x1B4a89A896E1471382CB172b1849BB2c91A4a522',
        token_index=0,
        reserve_token=0,
        reserve_eth=0
    ), 0.001, swap=True)

    logging.info(f"Simulation result {result}")
