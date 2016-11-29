# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enumeration', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='acct_no',
            field=models.CharField(max_length=16, unique=True, verbose_name='Account No.'),
        ),
        migrations.AlterField(
            model_name='account',
            name='book_code',
            field=models.CharField(max_length=8, verbose_name='Book Code'),
        ),
    ]
