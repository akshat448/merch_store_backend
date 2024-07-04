# Generated by Django 4.2.11 on 2024-07-04 10:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="quantity",
        ),
        migrations.AddField(
            model_name="cartitem",
            name="quantity",
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name="product",
            name="max_quantity",
            field=models.IntegerField(default=1),
        ),
    ]
