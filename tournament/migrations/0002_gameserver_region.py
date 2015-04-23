# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameserver',
            name='region',
            field=models.ForeignKey(null=True, blank=True, to='tournament.Region'),
        ),
    ]
