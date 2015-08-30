# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessOffice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('email', models.EmailField(max_length=50, blank=True)),
                ('phone', models.CharField(max_length=20, blank=True)),
                ('url', models.URLField(max_length=50, blank=True)),
                ('street1', models.CharField(max_length=50, blank=True)),
                ('street2', models.CharField(max_length=50, blank=True)),
                ('city', models.CharField(max_length=20)),
                ('note', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'business_office',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('email', models.EmailField(max_length=50, blank=True)),
                ('phone', models.CharField(max_length=20, blank=True)),
                ('url', models.URLField(max_length=50, blank=True)),
                ('street1', models.CharField(max_length=50, blank=True)),
                ('street2', models.CharField(max_length=50, blank=True)),
                ('city', models.CharField(max_length=20)),
                ('note', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'organization',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('code', models.CharField(max_length=2, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('capcity', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'state',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='organization',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.State'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='businessoffice',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.State'),
            preserve_default=True,
        ),
    ]
