# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20170407_2157'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='powerline',
            options={},
        ),
        migrations.AlterModelOptions(
            name='station',
            options={},
        ),
        migrations.AlterField(
            model_name='powerline',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=100),
        ),
        migrations.AlterField(
            model_name='station',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='powerline',
            unique_together=set([('name', 'type')]),
        ),
        migrations.AlterUniqueTogether(
            name='station',
            unique_together=set([('name', 'type')]),
        ),
    ]
