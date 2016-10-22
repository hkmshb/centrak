# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20161018_1817'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiServiceInfo',
            fields=[
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(null=True, auto_now=True)),
                ('key', models.CharField(serialize=False, max_length=20, primary_key=True, verbose_name='Service Key')),
                ('title', models.CharField(max_length=50, unique=True, verbose_name='Service Title')),
                ('description', models.TextField(blank=True, verbose_name='Service Description')),
                ('api_root', models.URLField(max_length=100, unique=True, verbose_name='API Root')),
                ('api_auth', models.URLField(max_length=100, blank=True, verbose_name='API Auth')),
                ('api_extra', models.URLField(max_length=100, blank=True, verbose_name='API Extra')),
                ('api_token', models.CharField(max_length=100, blank=True, verbose_name='API Token')),
                ('is_active', models.BooleanField(default=False, verbose_name='Is Active')),
            ],
            options={
                'db_table': 'apiservice_info',
            },
        ),
    ]
