# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('enumeration', '0006_auto_20150919_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammembership',
            name='device',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.PROTECT, to='enumeration.Device'),
            preserve_default=True,
        ),
    ]
