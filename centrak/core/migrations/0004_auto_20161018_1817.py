# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0003_auto_20161016_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Phone')),
            ],
        ),
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('page_size', models.PositiveSmallIntegerField(default=50, verbose_name='General Page Size')),
                ('capture_page_size', models.PositiveIntegerField(default=200, verbose_name='Capture Page Size')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='settings')),
            ],
        ),
        migrations.AlterModelOptions(
            name='businessoffice',
            options={'permissions': (('can_manage_region', 'Can add, change and delete Level1 objects'), ('can_import', 'Can import LEVEL2 objects.'), ('can_export', 'Can export LEVEL2 objects.')), 'ordering': ['level', 'name']},
        ),
        migrations.AlterModelOptions(
            name='powerline',
            options={'permissions': (('can_sync_data', 'Can pull in data from external service'), ('can_export', 'Can export entity data'))},
        ),
        migrations.AlterModelOptions(
            name='station',
            options={'permissions': (('can_sync_data', 'Can pull in data from external service'), ('can_export', 'Can export entity data'))},
        ),
        migrations.AddField(
            model_name='userprofile',
            name='location',
            field=models.ForeignKey(to='core.BusinessOffice', null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='profile'),
        ),
    ]
