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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=50)),
                ('email', models.EmailField(blank=True, max_length=50)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('url', models.URLField(blank=True, max_length=50)),
                ('street1', models.CharField(blank=True, max_length=50)),
                ('street2', models.CharField(blank=True, max_length=50)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=50)),
                ('email', models.EmailField(blank=True, max_length=50)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('url', models.URLField(blank=True, max_length=50)),
                ('street1', models.CharField(blank=True, max_length=50)),
                ('street2', models.CharField(blank=True, max_length=50)),
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
                ('code', models.CharField(serialize=False, max_length=2, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
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
