from django.db import models

# Create your models here.
class Block(models.Model):
    class Meta():
        db_table = 'block'

    id = models.BigAutoField(primary_key=True)
    block_number = models.BigIntegerField(unique=True)
    block_timestamp = models.BigIntegerField(null=True, default=0)
    base_fee = models.BigIntegerField(null=True, default=0)
    gas_used = models.BigIntegerField(null=True, default=0)
    gas_limit = models.BigIntegerField(null=True, default=0)

    created_at = models.DateTimeField(null=True,auto_now_add=True)
    updated_at = models.DateTimeField(null=True,auto_now=True)
    is_deleted = models.IntegerField(null=True,default=0)

    def __str__(self) -> str:
        return str(self.block_number)
    
class Transaction(models.Model):
    class Meta():
        db_table = 'transaction'

    id = models.BigAutoField(primary_key=True)
    tx_hash = models.CharField(max_length=66, unique=True)
    block = models.ForeignKey(Block, on_delete=models.DO_NOTHING)
    sender = models.CharField(max_length=42, null=True)
    to = models.CharField(max_length=42, null=True)    
    value = models.FloatField(null=True, default=0)
    gas_limit = models.FloatField(null=True, default=0)
    max_priority_fee_per_gas = models.FloatField(null=True, default=0)
    max_fee_per_gas = models.FloatField(null=True, default=0)
    status = models.IntegerField(null=True, default=0)

    created_at = models.DateTimeField(null=True,auto_now_add=True)
    updated_at = models.DateTimeField(null=True,auto_now=True)
    is_deleted = models.IntegerField(null=True,default=0)

    def __str__(self) -> str:
        return str(self.tx_hash)

class Pair(models.Model):
    class Meta():
        db_table = 'pair'

    id = models.BigAutoField(primary_key=True)
    address = models.CharField(max_length=42, unique=True)
    token = models.CharField(max_length=42)
    token_index = models.IntegerField(null=True, default=0)
    reserve_token = models.FloatField(null=True, default=0)
    reserve_eth = models.FloatField(null=True, default=0)
    deployed_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(null=True,auto_now_add=True)
    updated_at = models.DateTimeField(null=True,auto_now=True)
    is_deleted = models.IntegerField(null=True,default=0)

    def __str__(self) -> str:
        return f"{self.address}"
    
class Position(models.Model):
    class Meta():
        db_table = 'position'

    id = models.BigAutoField(primary_key=True)
    pair = models.ForeignKey(Pair, on_delete=models.DO_NOTHING)
    amount = models.FloatField(null=True, default=0)
    buy_price = models.FloatField(null=True, default=0)
    purchased_at = models.DateTimeField(null=True)
    is_liquidated = models.IntegerField(null=True, default=0)
    liquidated_at = models.DateTimeField(null=True)
    sell_price = models.FloatField(null=True, default=0)
    liquidation_attempts = models.IntegerField(null=True, default=0)
    pnl = models.FloatField(null=True, default=0)
    signer = models.CharField(max_length=42, null=True)
    bot = models.CharField(max_length=42, null=True)

    created_at = models.DateTimeField(null=True,auto_now_add=True)
    updated_at = models.DateTimeField(null=True,auto_now=True)
    is_deleted = models.IntegerField(null=True,default=0)

    def __str__(self) -> str:
        return f"{self.pair}"
    
class PositionTransaction(models.Model):
    class Meta():
        db_table = 'position_transaction'

    id = models.BigAutoField(primary_key=True)
    position = models.ForeignKey(Position, on_delete=models.DO_NOTHING)
    transaction = models.ForeignKey(Transaction, on_delete=models.DO_NOTHING)
    is_buy = models.IntegerField(null=True,default=0)

    created_at = models.DateTimeField(null=True,auto_now_add=True)
    updated_at = models.DateTimeField(null=True,auto_now=True)
    is_deleted = models.IntegerField(null=True,default=0)

    def __str__(self) -> str:
        return f"{self.pair}"
    
class BlackList(models.Model):
    class Meta():
        db_table = 'blacklist'

    id = models.BigAutoField(primary_key=True)
    reserve_eth = models.FloatField(unique=True)

    created_at = models.DateTimeField(null=True,auto_now_add=True)
    updated_at = models.DateTimeField(null=True,auto_now=True)
    is_deleted = models.IntegerField(null=True,default=0)

    def __str__(self) -> str:
        return f"{self.reserve_eth}"
    

