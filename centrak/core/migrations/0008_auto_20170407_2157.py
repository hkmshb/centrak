# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20170331_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='powerline',
            name='ext_id',
        ),
        migrations.RemoveField(
            model_name='powerline',
            name='source_station_ext_id',
        ),
        migrations.RemoveField(
            model_name='station',
            name='ext_id',
        ),
        migrations.RemoveField(
            model_name='station',
            name='source_powerline_ext_id',
        ),
        migrations.AddField(
            model_name='powerline',
            name='region',
            field=models.ForeignKey(blank=True, null=True, to='core.BusinessOffice'),
        ),
        migrations.AddField(
            model_name='station',
            name='region',
            field=models.ForeignKey(blank=True, null=True, to='core.BusinessOffice'),
        ),
    ]
