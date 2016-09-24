# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ezaddress', '__first__'),
        ('core', '0002_apiserviceinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessoffice',
            name='addr_raw',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='businessoffice',
            name='addr_state',
            field=models.ForeignKey(related_name='+', verbose_name='State', null=True, to='ezaddress.State', blank=True),
        ),
        migrations.AddField(
            model_name='businessoffice',
            name='addr_street',
            field=models.CharField(verbose_name='Street Address', max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='businessoffice',
            name='addr_town',
            field=models.CharField(verbose_name='Town/City', max_length=20, blank=True),
        ),
        migrations.AddField(
            model_name='businessoffice',
            name='altitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='businessoffice',
            name='gps_error',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='businessoffice',
            name='latitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='businessoffice',
            name='longitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='businessoffice',
            name='postal_code',
            field=models.CharField(verbose_name='Postal Code', max_length=10, blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='addr_raw',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='addr_state',
            field=models.ForeignKey(related_name='+', verbose_name='State', null=True, to='ezaddress.State', blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='addr_street',
            field=models.CharField(verbose_name='Street Address', max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='addr_town',
            field=models.CharField(verbose_name='Town/City', max_length=20, blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='altitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='gps_error',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='latitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='longitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='postal_code',
            field=models.CharField(verbose_name='Postal Code', max_length=10, blank=True),
        ),
    ]
