# Generated by Django 4.2.11 on 2024-07-11 14:59

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('discount_percentage', models.FloatField()),
                ('max_uses', models.IntegerField()),
                ('expiry_date', models.DateTimeField()),
                ('for_user_positions', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, default=list, size=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('custom', models.BooleanField(default=False)),
                ('uses', models.IntegerField(default=0)),
            ],
        ),
    ]
