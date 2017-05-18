# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-05-07 01:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('HealthNet', '0017_auto_20170505_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('new_doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='New_doctor', to='HealthNet.Doctor')),
            ],
        ),
        migrations.CreateModel(
            name='TransferRequestReply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acceptance_reply', models.SlugField(choices=[('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Pending', 'Pending')], default='Pending')),
                ('reason', models.TextField(max_length=200, null=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Receiver', to=settings.AUTH_USER_MODEL)),
                ('transfer_request', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='Transfer_request', to='HealthNet.TransferRequest')),
            ],
        ),
        migrations.RemoveField(
            model_name='patient',
            name='notes',
        ),
        migrations.AlterField(
            model_name='patient',
            name='hospital_status',
            field=models.SlugField(choices=[('Admitted', 'Admitted'), ('Not Admitted', 'Not Admitted')], default='Not Admitted'),
        ),
        migrations.DeleteModel(
            name='Note',
        ),
        migrations.AddField(
            model_name='transferrequest',
            name='patient_to_transfer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Transferring_Patient', to='HealthNet.Patient'),
        ),
        migrations.AddField(
            model_name='transferrequest',
            name='receiving_admin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Receiving_administrator', to='HealthNet.HospitalAdmin'),
        ),
        migrations.AddField(
            model_name='transferrequest',
            name='receiving_hospital',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Receiving_hospital', to='HealthNet.Hospital'),
        ),
        migrations.AddField(
            model_name='transferrequest',
            name='requester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Requester', to=settings.AUTH_USER_MODEL),
        ),
    ]