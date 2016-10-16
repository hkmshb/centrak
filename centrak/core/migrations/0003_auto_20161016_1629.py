# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ezaddress', '__first__'),
        ('core', '0002_core_initial_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='Powerline',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(null=True, auto_now=True)),
                ('code', models.CharField(unique=True, max_length=20, verbose_name='Code')),
                ('altcode', models.CharField(unique=True, max_length=20, blank=True, verbose_name='Alternative Code')),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('is_public', models.BooleanField(verbose_name='Is Public', default=True)),
                ('last_synced', models.DateTimeField(null=True, verbose_name='Last Synced')),
                ('ext_id', models.IntegerField(unique=True)),
                ('date_commissioned', models.DateField(null=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Feeder'), (2, 'Upriser')], verbose_name='Type')),
                ('voltage', models.PositiveSmallIntegerField(choices=[(5, '330KV'), (4, '132KV'), (3, '33KV'), (2, '11KV'), (1, '0.415KV')], verbose_name='Voltage')),
                ('line_length', models.IntegerField(null=True, verbose_name='Line Length', blank=True)),
                ('pole_count', models.IntegerField(null=True, verbose_name='Pole Count', blank=True)),
                ('source_station_ext_id', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('addr_raw', models.CharField(max_length=200, blank=True)),
                ('addr_street', models.CharField(verbose_name='Street Address', max_length=100, blank=True)),
                ('addr_town', models.CharField(verbose_name='Town/City', max_length=20, blank=True)),
                ('postal_code', models.CharField(verbose_name='Postal Code', max_length=10, blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
                ('altitude', models.FloatField(null=True, blank=True)),
                ('gps_error', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(null=True, auto_now=True)),
                ('code', models.CharField(unique=True, max_length=20, verbose_name='Code')),
                ('altcode', models.CharField(unique=True, max_length=20, blank=True, verbose_name='Alternative Code')),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('is_public', models.BooleanField(verbose_name='Is Public', default=True)),
                ('last_synced', models.DateTimeField(null=True, verbose_name='Last Synced')),
                ('ext_id', models.IntegerField(unique=True)),
                ('date_commissioned', models.DateField(null=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Transmission'), (2, 'Injection'), (3, 'Distribution')], verbose_name='Type')),
                ('voltage_ratio', models.PositiveSmallIntegerField(choices=[(6, '330/132KV'), (5, '132/33KV'), (4, '132/11KV'), (3, '33/11KV'), (2, '33/0.415KV'), (1, '11/0.415KV')], verbose_name='Voltage Ratio')),
                ('source_powerline_ext_id', models.IntegerField(null=True, blank=True)),
                ('addr_state', models.ForeignKey(null=True, blank=True, related_name='+', verbose_name='State', to='ezaddress.State')),
                ('source_powerline', models.ForeignKey(null=True, blank=True, to='core.Powerline')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='powerline',
            name='source_station',
            field=models.ForeignKey(null=True, blank=True, to='core.Station'),
        ),
    ]
