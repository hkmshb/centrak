# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enumeration', '0004_auto_20150902_2036'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberRole',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'enum_member_role',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('code', models.CharField(unique=True, max_length=20)),
                ('devices', models.ManyToManyField(to='enumeration.Device')),
            ],
            options={
                'db_table': 'enum_team',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TeamMembership',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('date_joined', models.DateField()),
                ('device', models.ForeignKey(to='enumeration.Device')),
                ('person', models.ForeignKey(to='enumeration.Person')),
                ('role', models.ForeignKey(to='enumeration.MemberRole')),
                ('team', models.ForeignKey(to='enumeration.Team')),
            ],
            options={
                'db_table': 'enum_team_membership',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(through='enumeration.TeamMembership', to='enumeration.Person'),
            preserve_default=True,
        ),
    ]
