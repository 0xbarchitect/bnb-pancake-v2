# Generated by Django 5.0.6 on 2024-08-08 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("console", "0004_blacklist"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blacklist",
            name="reserve_eth",
            field=models.FloatField(unique=True),
        ),
    ]