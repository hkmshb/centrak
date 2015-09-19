# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('enumeration', '0005_auto_20150911_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='date_created',
            field=models.DateField(auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='team',
            name='date_created',
            field=models.DateField(auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='teammembership',
            name='date_joined',
            field=models.DateField(auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='teammembership',
            name='device',
            field=models.ForeignKey(to='enumeration.Device', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='teammembership',
            name='person',
            field=models.ForeignKey(to='enumeration.Person', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='teammembership',
            name='role',
            field=models.CharField(choices=[('SP', 'Supervisor'), ('LD', 'Lead'), ('ST', 'Scout'), ('EN', 'Enumerator'), ('MK', 'Marker'), ('RC', 'Recorder'), ('MB', 'Member')], max_length=2, default='MB'),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='MemberRole',
        ),
        migrations.AlterField(
            model_name='teammembership',
            name='team',
            field=models.ForeignKey(to='enumeration.Team', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
    ]
