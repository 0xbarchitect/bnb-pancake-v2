# Generated by Django 5.0.6 on 2024-08-24 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("console", "0016_alter_pnl_timestamp"),
    ]

    operations = [
        migrations.AddField(
            model_name="pnl",
            name="number_failed",
            field=models.IntegerField(default=0, null=True),
        ),
    ]
