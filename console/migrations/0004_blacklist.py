# Generated by Django 5.0.6 on 2024-08-08 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("console", "0003_delete_watchinglist"),
    ]

    operations = [
        migrations.CreateModel(
            name="BlackList",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("reserve_eth", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("is_deleted", models.IntegerField(default=0, null=True)),
            ],
            options={
                "db_table": "blacklist",
            },
        ),
    ]