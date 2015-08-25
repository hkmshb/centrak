# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enumeration', '0002_auto_20150817_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='label',
            field=models.CharField(default='TXXXDY', max_length=10, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='device',
            name='notes',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='model',
            field=models.CharField(blank=True, max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='os_version',
            field=models.CharField(blank=True, max_length=25),
            preserve_default=True,
        ),
    ]
