# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('steamauth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='steamuser',
            name='level',
            field=models.PositiveSmallIntegerField(choices=[(9, 'Owner'), (6, 'Admin'), (3, 'Helper'), (1, 'User')], default=1),
        ),
    ]
