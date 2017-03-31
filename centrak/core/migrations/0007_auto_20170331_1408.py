# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessoffice',
            name='short_name',
            field=models.CharField(verbose_name='Short Name', default='', unique=True, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='businessoffice',
            name='uuid',
            field=models.UUIDField(verbose_name='UUID', editable=False, default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='organisation',
            name='uuid',
            field=models.UUIDField(verbose_name='UUID', editable=False, default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='powerline',
            name='uuid',
            field=models.UUIDField(verbose_name='UUID', editable=False, default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='station',
            name='uuid',
            field=models.UUIDField(verbose_name='UUID', editable=False, default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='short_name',
            field=models.CharField(verbose_name='Short Name', unique=True, max_length=20),
        ),
    ]
