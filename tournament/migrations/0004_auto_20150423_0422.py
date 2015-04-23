# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0003_auto_20150423_0420'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournament',
            name='ends_at',
        ),
        migrations.RemoveField(
            model_name='tournament',
            name='ladder_rounds',
        ),
        migrations.RemoveField(
            model_name='tournament',
            name='playoff_rounds',
        ),
        migrations.RemoveField(
            model_name='tournament',
            name='starts_at',
        ),
        migrations.RemoveField(
            model_name='tournament',
            name='state',
        ),
        migrations.AddField(
            model_name='season',
            name='ends_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='season',
            name='ladder_rounds',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='season',
            name='playoff_rounds',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='season',
            name='starts_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='season',
            name='state',
            field=models.CharField(max_length=1, choices=[('O', 'Open'), ('C', 'Closed'), ('P', 'Pending'), ('I', 'In progress'), ('F', 'Finished')], default='O'),
        ),
    ]
