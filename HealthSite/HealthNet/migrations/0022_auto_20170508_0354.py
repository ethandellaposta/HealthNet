# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-05-08 03:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HealthNet', '0021_auto_20170507_1318'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='image',
        ),
        migrations.AlterField(
            model_name='doctor',
            name='confirm_password',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='hospitaladmin',
            name='confirm_password',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='message',
            name='msg_content',
            field=models.TextField(max_length=200, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='nurse',
            name='confirm_password',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='patient',
            name='confirm_password',
            field=models.CharField(default='', max_length=20),
        ),
    ]