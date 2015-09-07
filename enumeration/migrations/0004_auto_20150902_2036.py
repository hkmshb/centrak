# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150902_1147'),
        ('enumeration', '0003_auto_20150825_2056'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('gender', models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], default='M')),
                ('official_status', models.CharField(max_length=2, choices=[('FS', 'Full Staff'), ('CS', 'Contract Staff'), ('YC', 'Youth Corper'), ('IT', 'Industrial Trainee')], default='FS')),
                ('mobile', models.CharField(max_length=20)),
                ('mobile2', models.CharField(max_length=20, blank=True)),
                ('email', models.EmailField(max_length=50)),
                ('location', models.ForeignKey(to='core.BusinessOffice', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'enum_person',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='person',
            unique_together=set([('first_name', 'last_name')]),
        ),
    ]
