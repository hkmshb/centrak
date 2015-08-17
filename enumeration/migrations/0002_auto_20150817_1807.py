# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enumeration', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=50)),
                ('os_version', models.CharField(max_length=25)),
                ('form_factor', models.CharField(max_length=1, default='P', choices=[('P', 'Phone'), ('T', 'Tablet')])),
                ('serialno', models.CharField(max_length=25, blank=True)),
                ('brand', models.ForeignKey(to='enumeration.Manufacturer')),
                ('mobile_os', models.ForeignKey(to='enumeration.MobileOS')),
            ],
            options={
                'db_table': 'enum_device',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeviceIMEI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.CharField(max_length=25, unique=True)),
                ('device', models.ForeignKey(to='enumeration.Device')),
            ],
            options={
                'db_table': 'enum_device_imei',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='mobileos',
            name='provider',
            field=models.CharField(max_length=50, blank=True, default=''),
            preserve_default=True,
        ),
    ]
