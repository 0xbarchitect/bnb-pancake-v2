# Generated by Django 5.0.6 on 2024-08-14 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("console", "0007_remove_blacklist_reserve_eth_blacklist_address_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="pair",
            index=models.Index(fields=["address"], name="pair_address_1079d9_idx"),
        ),
    ]