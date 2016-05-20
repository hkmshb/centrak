# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import ezaddress.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessLevel',
            fields=[
                ('code', models.CharField(primary_key=True, max_length=2, verbose_name='Code', serialize=False, choices=[('L1', 'Level 1'), ('L2', 'Level 2'), ('L3', 'Level 3')])),
                ('name', models.CharField(unique=True, max_length=20, verbose_name='Name')),
            ],
            options={
                'db_table': 'business_level',
            },
        ),
        migrations.CreateModel(
            name='BusinessOffice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(auto_now=True, null=True)),
                ('name', models.CharField(unique=True, max_length=40, verbose_name='Name')),
                ('email', models.EmailField(max_length=100, blank=True, verbose_name='Email')),
                ('phone', models.CharField(max_length=20, blank=True, verbose_name='Phone')),
                ('website', models.CharField(max_length=100, blank=True, verbose_name='Website')),
                ('code', models.CharField(unique=True, max_length=5, verbose_name='Code')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, verbose_name='Level', to='core.BusinessLevel')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, verbose_name='Parent Office', to='core.BusinessOffice')),
            ],
            options={
                'db_table': 'business_office',
                'ordering': ['level', 'name'],
            },
            bases=(models.Model, ezaddress.models.AddressGPSMixin),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(auto_now=True, null=True)),
                ('name', models.CharField(unique=True, max_length=40, verbose_name='Name')),
                ('email', models.EmailField(max_length=100, blank=True, verbose_name='Email')),
                ('phone', models.CharField(max_length=20, blank=True, verbose_name='Phone')),
                ('website', models.CharField(max_length=100, blank=True, verbose_name='Website')),
            ],
            options={
                'db_table': 'organization',
            },
            bases=(models.Model, ezaddress.models.AddressGPSMixin),
        ),
    ]
