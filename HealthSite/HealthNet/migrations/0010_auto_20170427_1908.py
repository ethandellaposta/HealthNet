# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-04-27 19:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('HealthNet', '0009_auto_20170427_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='testDate',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
