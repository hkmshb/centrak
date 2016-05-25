# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(auto_now=True, null=True)),
                ('title', models.CharField(unique=True, verbose_name='Title', max_length=30)),
                ('description', models.TextField(verbose_name='Description', null=True)),
                ('status', models.PositiveSmallIntegerField(verbose_name='Status', choices=[(1, 'In View'), (2, 'In Progress'), (3, 'Concluded'), (4, 'Revisited')], default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('date_started', models.DateField(verbose_name='Start Date')),
                ('date_ended', models.DateField(verbose_name='End Date')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProjectXForm',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('project', models.ForeignKey(to='enumeration.Project')),
            ],
        ),
        migrations.CreateModel(
            name='XForm',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(auto_now=True, null=True)),
                ('object_id', models.PositiveIntegerField(unique=True, verbose_name='ID')),
                ('id_string', models.CharField(unique=True, verbose_name='ID String/Code', max_length=30)),
                ('title', models.CharField(unique=True, verbose_name='Title', max_length=50)),
                ('type', models.CharField(verbose_name='Type', max_length=1)),
                ('description', models.TextField(verbose_name='Description', null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('api_url', models.URLField(verbose_name='API Url', max_length=100)),
                ('synced_by', models.CharField(max_length=50)),
                ('last_synced', models.DateTimeField(null=True)),
                ('date_imported', models.DateField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='projectxform',
            name='xform',
            field=models.OneToOneField(to='enumeration.XForm'),
        ),
    ]
