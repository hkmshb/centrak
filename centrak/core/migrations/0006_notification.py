# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_apiserviceinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(auto_now=True, null=True)),
                ('message', models.TextField(verbose_name='Message')),
                ('read', models.BooleanField(verbose_name='Read', default=False)),
                ('task_id', models.CharField(verbose_name='Task Id', max_length=100, blank=True)),
                ('task_status', models.CharField(verbose_name='Task Status', max_length=32, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
