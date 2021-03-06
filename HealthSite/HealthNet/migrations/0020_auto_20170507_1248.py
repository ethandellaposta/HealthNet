# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-05-07 12:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('HealthNet', '0019_patient_confirm_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=50)),
                ('date', models.DateTimeField()),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='User_who_did_action', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Entry',
                'verbose_name_plural': 'Entries',
            },
        ),
        migrations.CreateModel(
            name='TimeFrame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startTime', models.DateTimeField()),
                ('endTime', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='patient',
            name='current_medications',
            field=models.CharField(default='', max_length=250),
        ),
        migrations.AddField(
            model_name='patient',
            name='known_allergies',
            field=models.CharField(default='', max_length=250),
        ),
        migrations.AddField(
            model_name='patient',
            name='medical_conditions',
            field=models.CharField(default='', max_length=250),
        ),
    ]
