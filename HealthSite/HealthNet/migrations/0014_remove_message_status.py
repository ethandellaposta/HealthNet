# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-05-05 16:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HealthNet', '0013_message_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='status',
        ),
    ]
