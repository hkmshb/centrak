# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(null=True, auto_now=True)),
                ('acct_no', models.CharField(unique=True, max_length=13, verbose_name='Account No.')),
                ('book_code', models.CharField(max_length=6, verbose_name='Book Code')),
                ('cust_name', models.CharField(max_length=100, verbose_name='Customer Name')),
                ('cust_mobile', models.CharField(null=True, blank=True, max_length=20, verbose_name='Mobile')),
                ('acct_status', models.CharField(null=True, blank=True, choices=[('A', 'Active'), ('I', 'Inactive')], max_length=3, verbose_name='Status')),
                ('tariff', models.CharField(choices=[('R1', 'R1'), ('R2A', 'R2A'), ('R2B', 'R2B'), ('R3', 'R3'), ('R4', 'R4'), ('C1A', 'C1A'), ('C1B', 'C1B'), ('C2', 'C2'), ('C3', 'C3'), ('D1', 'D1'), ('D2', 'D2'), ('D3', 'D3'), ('A1', 'A1'), ('A2', 'A2'), ('A3', 'A3'), ('L1', 'L1')], max_length=5, verbose_name='Tariff')),
                ('meter_no', models.CharField(null=True, blank=True, max_length=20, verbose_name='Meter No.')),
                ('service_addr', models.CharField(null=True, blank=True, max_length=150, verbose_name='Service Address')),
            ],
            options={
                'db_table': 'enum_account',
            },
        ),
    ]
