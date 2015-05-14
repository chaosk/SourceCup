# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0006_auto_20150514_0716'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='entry_code',
            field=models.CharField(blank=True, max_length=25),
        ),
    ]
