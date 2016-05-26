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
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(auto_now=True, null=True)),
                ('title', models.CharField(verbose_name='Title', unique=True, max_length=30)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('status', models.PositiveSmallIntegerField(verbose_name='Status', default=1, choices=[(1, 'In View'), (2, 'In Progress'), (3, 'Concluded'), (4, 'Revisited')])),
                ('is_active', models.BooleanField(default=True)),
                ('date_started', models.DateField(verbose_name='Start Date')),
                ('date_ended', models.DateField(verbose_name='End Date', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProjectXForm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('project', models.ForeignKey(to='enumeration.Project')),
            ],
        ),
        migrations.CreateModel(
            name='XForm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(auto_now=True, null=True)),
                ('object_id', models.PositiveIntegerField(verbose_name='ID', unique=True)),
                ('id_string', models.CharField(verbose_name='ID String/Code', unique=True, max_length=30)),
                ('title', models.CharField(verbose_name='Title', unique=True, max_length=50)),
                ('type', models.CharField(verbose_name='Type', choices=[('C', 'Capture XForm'), ('U', 'Update XForm')], blank=True, max_length=1)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('is_active', models.BooleanField(default=False)),
                ('api_url', models.URLField(verbose_name='API Url', blank=True, max_length=100)),
                ('synced_by', models.CharField(blank=True, max_length=50)),
                ('last_synced', models.DateTimeField(blank=True, null=True)),
                ('date_imported', models.DateField(blank=True, null=True)),
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
