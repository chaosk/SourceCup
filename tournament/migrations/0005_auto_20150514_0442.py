# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0004_auto_20150423_0422'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membership',
            options={'get_latest_by': 'joined_at'},
        ),
        migrations.AlterModelOptions(
            name='teamentry',
            options={'verbose_name_plural': 'Team Entries'},
        ),
        migrations.AddField(
            model_name='team',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 5, 14, 2, 42, 39, 871581, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
