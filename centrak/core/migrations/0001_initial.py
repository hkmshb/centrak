# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ezaddress', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessLevel',
            fields=[
                ('code', models.CharField(serialize=False, verbose_name='Code', choices=[('L1', 'Level-1'), ('L2', 'Level-2'), ('L3', 'Level-3')], primary_key=True, max_length=2)),
                ('name', models.CharField(verbose_name='Name', unique=True, max_length=20)),
            ],
            options={
                'db_table': 'business_level',
            },
        ),
        migrations.CreateModel(
            name='BusinessOffice',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('addr_raw', models.CharField(blank=True, max_length=200)),
                ('addr_street', models.CharField(verbose_name='Street Address', blank=True, max_length=100)),
                ('addr_town', models.CharField(verbose_name='Town/City', blank=True, max_length=20)),
                ('postal_code', models.CharField(verbose_name='Postal Code', blank=True, max_length=10)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('altitude', models.FloatField(blank=True, null=True)),
                ('gps_error', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(auto_now=True, null=True)),
                ('name', models.CharField(verbose_name='Name', unique=True, max_length=40)),
                ('email', models.EmailField(verbose_name='Email', blank=True, max_length=100)),
                ('phone', models.CharField(verbose_name='Phone', blank=True, max_length=20)),
                ('website', models.URLField(verbose_name='Website', blank=True, max_length=100)),
                ('code', models.CharField(verbose_name='Code', unique=True, max_length=12)),
                ('category', models.CharField(verbose_name='Category', choices=[('CSP', 'Customer Service Point'), ('TSP', 'Technical Service Point')], blank=True, max_length=5)),
                ('addr_state', models.ForeignKey(verbose_name='State', blank=True, to='ezaddress.State', related_name='+', null=True)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Level', to='core.BusinessLevel', null=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Parent Office', blank=True, to='core.BusinessOffice', null=True)),
            ],
            options={
                'db_table': 'business_office',
                'ordering': ['level', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('addr_raw', models.CharField(blank=True, max_length=200)),
                ('addr_street', models.CharField(verbose_name='Street Address', blank=True, max_length=100)),
                ('addr_town', models.CharField(verbose_name='Town/City', blank=True, max_length=20)),
                ('postal_code', models.CharField(verbose_name='Postal Code', blank=True, max_length=10)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('altitude', models.FloatField(blank=True, null=True)),
                ('gps_error', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(auto_now=True, null=True)),
                ('name', models.CharField(verbose_name='Name', unique=True, max_length=40)),
                ('email', models.EmailField(verbose_name='Email', blank=True, max_length=100)),
                ('phone', models.CharField(verbose_name='Phone', blank=True, max_length=20)),
                ('website', models.URLField(verbose_name='Website', blank=True, max_length=100)),
                ('short_name', models.CharField(verbose_name='Short Name', blank=True, max_length=20)),
                ('addr_state', models.ForeignKey(verbose_name='State', blank=True, to='ezaddress.State', related_name='+', null=True)),
            ],
            options={
                'db_table': 'organisation',
            },
        ),
    ]
