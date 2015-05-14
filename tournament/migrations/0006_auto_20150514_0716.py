# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0005_auto_20150514_0442'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membership',
            options={'ordering': ['joined_at'], 'get_latest_by': 'joined_at'},
        ),
        migrations.AddField(
            model_name='tournament',
            name='teams',
            field=models.ManyToManyField(to='tournament.Team', blank=True, through='tournament.TeamEntry', related_name='tournaments'),
        ),
    ]
