# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0002_gameserver_region'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tournament',
            unique_together=set([('season', 'region')]),
        ),
    ]
