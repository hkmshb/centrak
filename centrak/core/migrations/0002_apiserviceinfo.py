# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiServiceInfo',
            fields=[
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(auto_now=True, null=True)),
                ('key', models.CharField(verbose_name='Service Key', primary_key=True, serialize=False, max_length=30)),
                ('api_root', models.URLField(verbose_name='API Root', unique=True, max_length=100)),
                ('api_token', models.CharField(verbose_name='API Token', blank=True, max_length=100)),
            ],
            options={
                'db_table': 'apiservice_info',
            },
        ),
    ]
