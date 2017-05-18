# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-04-17 18:28
from __future__ import unicode_literals

import datetime
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Appointment Time')),
                ('accept_state', models.SlugField(default='Pending', max_length=10)),
                ('reason', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True, verbose_name='Gender')),
            ],
            options={
                'verbose_name': 'Doctor',
                'verbose_name_plural': 'Doctors',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='HospitalAdmin',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True, verbose_name='Gender')),
                ('hptal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HealthNet.Hospital', verbose_name='Hospital')),
            ],
            options={
                'verbose_name': 'Hospital Administrator',
                'verbose_name_plural': 'Hospital Administrators',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date')),
                ('user', models.TextField(verbose_name='User')),
                ('note', models.TextField(verbose_name='Note')),
            ],
        ),
        migrations.CreateModel(
            name='Nurse',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True, verbose_name='Gender')),
                ('hospital', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nurses', to='HealthNet.Hospital')),
            ],
            options={
                'verbose_name': 'Nurse',
                'verbose_name_plural': 'Nurses',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('medical_history', models.CharField(max_length=250)),
                ('insurance_information', models.CharField(default='None', max_length=250)),
                ('street', models.CharField(max_length=30)),
                ('city', models.CharField(max_length=30)),
                ('state', models.CharField(max_length=30)),
                ('country', models.CharField(max_length=30)),
                ('zip', models.CharField(max_length=30)),
                ('emergency_cname', models.CharField(max_length=30, verbose_name='Emergency Contact Name')),
                ('emergency_cnumber', models.CharField(max_length=10, verbose_name='Emergency Contact Number')),
                ('number', models.CharField(max_length=10)),
                ('hospital_status', models.CharField(max_length=30)),
                ('hospital', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hospital_patients', to='HealthNet.Hospital')),
                ('notes', models.ManyToManyField(blank=True, to='HealthNet.Note')),
                ('patient_doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_patients', to='HealthNet.Doctor')),
            ],
            options={
                'verbose_name': 'Patient',
                'verbose_name_plural': 'Patients',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prescription_name', models.CharField(max_length=250)),
                ('description', models.CharField(max_length=500)),
                ('datePrescribed', models.DateField(default=datetime.date.today, verbose_name='Date Prescribed')),
                ('doctorAssigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Prescribing_Doctor', to='HealthNet.Doctor')),
                ('patientAssigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Prescribed_Patient', to='HealthNet.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('results', models.TextField()),
                ('image', models.FileField(default='pic_folder/None/no-img.jpg', upload_to='static/pic_folder')),
                ('release', models.BooleanField(default=False)),
                ('testDate', models.DateTimeField(default=datetime.datetime(2017, 4, 17, 18, 28, 28, 818100))),
                ('testDoctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HealthNet.Doctor')),
                ('testPatient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HealthNet.Patient')),
            ],
            options={
                'verbose_name': 'Test',
                'verbose_name_plural': 'Tests',
            },
        ),
        migrations.AddField(
            model_name='doctor',
            name='hospital',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctors', to='HealthNet.Hospital'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Doctor', to='HealthNet.Doctor'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Patient', to='HealthNet.Patient'),
        ),
    ]