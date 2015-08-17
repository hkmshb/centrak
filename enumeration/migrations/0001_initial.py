# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=25)),
            ],
            options={
                'db_table': 'enum_manufacturer',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MobileOS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=25)),
                ('provider', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'enum_mobileos',
            },
            bases=(models.Model,),
        ),
    ]
