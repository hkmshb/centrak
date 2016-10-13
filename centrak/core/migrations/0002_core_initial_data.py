# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def _load_data_fixtures(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "addr_states_ng")
    call_command("loaddata", "core_initial_data")


class Migration(migrations.Migration):

    dependencies = [
        ('ezaddress', '__first__'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(_load_data_fixtures),
    ]
