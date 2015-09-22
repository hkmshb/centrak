# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('enumeration', '0007_auto_20150920_0024'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('is_active', models.BooleanField(default=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('note', models.TextField(blank=True)),
                ('supervisor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='enumeration.Person')),
                ('teams', models.ManyToManyField(to='enumeration.Team')),
            ],
            options={
                'db_table': 'enum_group',
            },
            bases=(models.Model,),
        ),
    ]
