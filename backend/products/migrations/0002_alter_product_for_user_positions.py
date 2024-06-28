# Generated by Django 4.2.11 on 2024-06-25 12:03

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="for_user_positions",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=20),
                default=list,
                help_text="List of roles/positions that can view this product.",
                size=None,
            ),
        ),
    ]
