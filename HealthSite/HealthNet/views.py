"""
    File contains all views associated with the implementation of HealthNet

    @authors: Theodora Bendlin, Ethan Della Posta, Laura Corrigan, Benjamin Kirby,
                Eliott Frilet
"""
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from . import models
from . import forms
from .models import Appointment, Doctor, Patient, HospitalAdmin, Nurse, Test, Prescription, Message, Hospital, \
    TransferRequest, TransferRequestReply, LogEntry
import datetime
from django.utils.safestring import mark_safe
from django.views import generic
from .forms import EditAppointmentForm, CreateAppointmentForm, CreateTestForm, NewMessageForm
from django.core.urlresolvers import reverse
from .calendar import Month, ApptCalendar, DoctorCalendar
from django.utils import timezone
from itertools import chain
import csv


def get_user_type(user):
    admin = False
    patient = False
    doctor = False
    nurse = False
    hosp = None
    app = []
    if Patient.objects.filter(pk=user.pk):
        patient = True
        p = Patient.objects.get(pk=user.pk)
        for a in Appointment.objects.all():
            if a.patient_id == p.id and a.accept_state != Appointment.REJECTED:
                app.append(a)
                app.sort(key=lambda b: b.appointment_time)
    elif Doctor.objects.filter(pk=user.pk):
        doctor = True
        d = Doctor.objects.get(pk=user.pk)
        for a in Appointment.objects.all():
            if a.doctor_id == d.id and a.accept_state != Appointment.REJECTED:
                app.append(a)
                app.sort(key=lambda b: b.appointment_time)
    elif Nurse.objects.filter(pk=user.pk):
        nurse = True
        n = Nurse.objects.get(pk=user.pk)
        for a in Appointment.objects.all():
            if a.doctor.hospital_id == n.hospital_id and a.accept_state != Appointment.REJECTED:
                app.append(a)
                app.sort(key=lambda b: b.appointment_time)
    elif HospitalAdmin.objects.filter(pk=user.pk):
        admin = True
        admin_temp = models.HospitalAdmin.objects.get(pk=user.id)
        hosp = admin_temp.hptal
    some = app.__len__() != 0


            #  0       1     2     3     4    5
    users = [patient,doctor,nurse,admin,hosp,app,some]
    return users

def base(request):
    """
        Base view for the user
    :param request: request for view
    :return: rendering of base view from template
    """

    user = request.user
    users = get_user_type(user)
    some_m = False
    base = True

    new_messages = []

    if users[0] or users[1] or users[2] or users[3]:
        for m in Message.objects.filter(receiver=user):
            if not m.status:
                new_messages.append(m)
                some_m = True

    transfers = TransferRequest.objects.order_by('patient_to_transfer__last_name').filter(
        receiving_admin__id = user.id
    )

    transferReqs = []

    for transfer in transfers:
        possible_replies = TransferRequestReply.objects.get(transfer_request__id = transfer.id)
        if( possible_replies.acceptance_reply == TransferRequestReply.PENDING):
            transferReqs.append(transfer)

    transferReplies = TransferRequestReply.objects.order_by('transfer_request__patient_to_transfer__last_name').filter(
        receiver__id = user.id
    )

    return render(request, 'base.html', {'user': user, "admin": users[3], "patient": users[0], 'hosp':users[4],
                                         'doctor':users[1], 'nurse':users[2], 'apps': users[5], 'some':users[6], 'new_messages':new_messages, 'some_m':some_m, 'transferReqs': transferReqs,
                                         'transferReplies': transferReplies, 'base':base, 'entries': LogEntry.objects.all(),
                                         'now': timezone.now(), '24HoursAgo': datetime.datetime.now()-datetime.timedelta(days=1)})

def baseCalendar(request):
    """
            Initial index view that automatically redirects to a
            calendar view of the current month and year
        :param request: GET calendar
        :return: Redirect to calendar view of current month and year
        """

    if not HospitalAdmin.objects.filter(pk=request.user.id):
        month = datetime.date.today().month
        year = datetime.date.today().year

        return HttpResponseRedirect(reverse('calendar', args=[month, year]))
    else:
        return render_to_response('error.html')

def patient_new(request):
    """
        View for registering a new patient. Uses a creation form provided in the
        forms.py file to complete registration
    :param request: request to register a new patient
    :return: rendering of the patient creation form
    """
    if request.method == 'POST':
        form = forms.PatientForm(request.POST)
        if form.is_valid():
            form.save()
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            user = authenticate(username=username, password=password)
            messages.success(request,  user.username + ' successfully registered!')
            log = LogEntry(requester=user, action="Patient Account Creation: " + username, date=datetime.datetime.now())
            log.save()
            if user:
                login(request, user)
                return redirect('base')
        form.fields['patient_doctor'].label_from_instance = lambda obj: "%s %s" % (obj, "(" + obj.hospital.name + ")")

    else:
        form = forms.PatientForm()
        form.fields['patient_doctor'].label_from_instance = lambda obj: "%s %s" % (obj, "(" + obj.hospital.name + ")")
    return render(request, 'patient_new.html', {'form': form})

def admin_patient_new(request):
    """
        View for registering a new patient from admin account. Uses a creation form provided in the
        forms.py file to complete registration
    :param request: request to register a new patient
    :return: rendering of the patient creation form
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        ex = 'Hospital'
        users = []
        user = request.user
        if request.method == 'POST':
            form = forms.PatientForm(request.POST)
            if form.is_valid():
                form.save()
                password = form.cleaned_data['password']
                username = form.cleaned_data['username']
                user = authenticate(username=username, password=password)
                messages.success(request, 'successfully registered patient!')
                log = LogEntry(requester=request.user, action="Patient Account Creation: " + username,
                               date=datetime.datetime.now())
                log.save()
                if user:
                    return redirect('patients')
            users = get_user_type(user)
        else:
            users = get_user_type(user)
            admin = HospitalAdmin.objects.get(pk=user.id)
            hospital = admin.hptal
            hosp = admin.hptal
            form = forms.PatientForm({'hospital': hosp})

            form.fields['patient_doctor'].queryset = Doctor.objects.filter(hospital_id=hosp)
        return render(request, 'patient_new.html', {'form': form, 'user': user, "admin": users[3], "patient": users[0], 'hosp': users[4],
                                                 'doctor': users[1], 'nurse': users[2], 'ex':ex})
    else:
        return render_to_response('error.html')



def doctor_new(request):
    """
        View for registering a new doctor. Uses a creation form provided in the
        forms.py file to complete registration
    :param request: request to register a new doctor
    :return: rendering of the doctor creation form
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        ex = 'Hospital'
        if request.method == 'POST':
            form = forms.DoctorForm(request.POST)
            if form.is_valid():
                form.save()
                password = form.cleaned_data['password']
                username = form.cleaned_data['username']
                user = authenticate(username=username, password=password)
                messages.success(request, ' successfully registered doctor!')
                log = LogEntry(requester=request.user, action="Doctor Account Creation: " + username,
                               date=datetime.datetime.now())
                log.save()
                if user:
                    return redirect('employees')
        else:
            user = request.user
            hospital = HospitalAdmin.objects.get(pk=user.id).hptal
            form = forms.DoctorForm({'hospital': hospital})
        user = request.user
        users = get_user_type(user)
        return render(request, 'doctor_new.html', {'form': form, 'admin': users[3], 'patient':users[0], 'ex': ex})
    else:
        return render_to_response('error.html')

def admin_new(request):
    """
        View for registering a new admin. Uses a creation form provided in the
        forms.py file to complete registration
    :param request: request to register a new admin
    :return: rendering of the admin creation form
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        ex = 'Hospital'
        if request.method == 'POST':
            form = forms.HNAdminForm(request.POST)
            if form.is_valid():
                form.save()
                password = form.cleaned_data['password']
                username = form.cleaned_data['username']
                user = authenticate(username=username, password=password)
                messages.success(request,  user.username + ' successfully registered admin!')
                log = LogEntry(requester=request.user, action="Admin Account Creation: " + username,
                               date=datetime.datetime.now())
                log.save()
                if user:
                    return redirect('employees')
        else:
            user = request.user
            hospital = HospitalAdmin.objects.get(pk=user.id).hptal
            form = forms.HNAdminForm({'hptal': hospital})
        user = request.user
        users = get_user_type(user)
        return render(request, 'admin_new.html', {'form': form, 'admin': users[3], 'patient':users[0], 'ex': ex})
    else:
        return render_to_response('error.html')

def nurse_new(request):
    """
        View for registering a new doctor. Uses a creation form provided in the
        forms.py file to complete registration
    :param request: request to register a new doctor
    :return: rendering of the doctor creation form
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        ex = 'Hospital'
        if request.method == 'POST':
            form = forms.NurseForm(request.POST)
            if form.is_valid():
                form.save()
                password = form.cleaned_data['password']
                username = form.cleaned_data['username']
                user = authenticate(username=username, password=password)
                messages.success(request,  user.username + ' successfully registered nurse!')
                log = LogEntry(requester=request.user, action="Nurse Account Creation: " + username,
                               date=datetime.datetime.now())
                log.save()
                if user:
                    return redirect('employees')
        else:
            user = request.user
            hospital = HospitalAdmin.objects.get(pk=user.id).hptal
            form = forms.NurseForm({'hospital': hospital})
        user = request.user
        users = get_user_type(user)
        return render(request, 'nurse_new.html', {'form': form, 'admin': users[3], 'patient':users[0], 'ex': ex})
    else:
        return render_to_response('error.html')

def logout_user(request):
    """
       Logs a patient out of the system
    :param request:
    :return: Redirect to the index of HealthNet
    """

    logout(request)
    return redirect('base')

def calendar(request, themonth, theyear):
    """
        Renders the calendar specific to the user requesting it. If the
        user is a patient or a doctor, he/she can only see their own
        appointments. If the user is a nurse, then he/she can see all of
        the appointments
    :param request: request to view the calendar
    :param themonth: (str) the current month
    :param theyear: (str) the current year
    :return: a rendering of the user-unique calendar
    """
    if Patient.objects.filter(pk=request.user.id) or Doctor.objects.filter(pk=request.user.id) or Nurse.objects.filter(pk=request.user.id):
        month = int(themonth)
        year = int(theyear)
        doctor = False
        nurse = False
        patient = False

        if((month < 1) or (month > 12) or (year < 1900)):
            return HttpResponseNotFound('<h1>Not a valid month/year</h1>')

        user = request.user

        if (Patient.objects.filter(pk=user.pk)):
            my_appointments = Appointment.objects.order_by('appointment_time').filter(
                appointment_time__year=year, appointment_time__month=month, patient__username=user.username,
            )
            cal = ApptCalendar(month, year, my_appointments)
            patient = True

        elif (Doctor.objects.filter(pk=user.pk)):
            my_appointments = Appointment.objects.order_by('appointment_time').filter(
                appointment_time__year=year, appointment_time__month=month, doctor__username=user.username,
            )
            cal = DoctorCalendar(month, year, my_appointments)
            doctor = True

        else:
            nurse = Nurse.objects.get(pk=user.id)
            hospital = nurse.hospital_id
            my_appointments = Appointment.objects.order_by('appointment_time').filter(
                appointment_time__year=year, appointment_time__month=month, doctor__hospital_id=hospital
            )
            cal = ApptCalendar(month, year, my_appointments)
            nurse = True

        calMonth = cal.format_month(month, year)

        # get the previous month and year to get the correct link in template
        prevYear = year
        prevMonth = month - 1
        if (prevMonth < 1):
            prevMonth = 12
            prevYear -= 1
        prevMonthName = cal.months[prevMonth]

        # get the next month and year to get the correct link in template
        nextYear = year
        nextMonth = month + 1
        if (nextMonth > 12):
            nextMonth = 1
            nextYear += 1
        nextMonthName = cal.months[nextMonth]
        is_calendar = True

        return render_to_response('calendar.html', {
            'calendar': cal,
            'month_format': mark_safe(calMonth),
            'month': cal.months[month],
            'year': str(year),
            'prevMonth': str(prevMonth),
            'prevYear': str(prevYear),
            'prevMonthName': prevMonthName,
            'nextMonth': str(nextMonth),
            'nextYear': str(nextYear),
            'nextMonthName': nextMonthName,
            'patient': patient, 'doctor': doctor, 'nurse': nurse, 'is_calendar':is_calendar
        })
    else:
        return render_to_response('error.html')


def day_view(request, day, month, year):
    """
        Detail view for viewing the appointments for a specific day
    :param request: GET
    :param day: Day in current month and year to look at
    :return: Rendering of the appointments
    """
    day = int(day)
    month = int(month)
    year = int(year)
    doctor = False
    nurse = False
    patient = False

    # making sure the inputs for month, day and year are valid
    if ((month < 1) or (month > 12) or (year < 1900) or (day > Month.days_in_month[month-1]) or (day < 1)):
        return HttpResponseNotFound('<h1>Not a valid month/year/day</h1>')

    user = request.user
    template = 'listAppointments.html'

    if (Patient.objects.filter(pk=user.pk)):
        my_appointments = Appointment.objects.order_by('appointment_time').filter(
            appointment_time__year=year, appointment_time__month=month, patient__username=user.username,
            appointment_time__day=day
        )
        patient = True

    elif (Doctor.objects.filter(pk=user.pk)):
        my_appointments = Appointment.objects.order_by('appointment_time').filter(
            appointment_time__year=year, appointment_time__month=month, doctor__username=user.username,
            appointment_time__day=day,
        )

        my_appointments = my_appointments.exclude(accept_state=Appointment.REJECTED)

        template = 'listAppointmentsDoctor.html'
        doctor = True

    else:
        my_appointments = Appointment.objects.order_by('appointment_time').filter(
            appointment_time__year=year, appointment_time__month=month,
            appointment_time__day=day
        )
        nurse = True

    return render_to_response(template, {
        'appointments': my_appointments,
        'themonth': month,
        'theyear': year,
        'theday': day,
        'patient': patient, 'doctor': doctor, 'nurse': nurse
    })

def patient_info(request):
    """
        Detail screen for rendering the patient's info
    :param request: request to view patient profile
    :return: rendering of the patient screen or the login screen
            if the user is an anonymous user
    """
    user = request.user
    if Patient.objects.filter(pk=user.id):
        patient = models.Patient.objects.get(pk=user.id)
        enumber = patient.number_format(patient.emergency_cnumber)
        number = patient.number_format(patient.number)
        return render_to_response('patient_info.html', {"user": user, "patient":patient, "enumber":enumber,
                                                        "number":number})
    else:
        return render_to_response('error.html')


def employees(request):
    """
        allow hospital admin to either register nurses or doctors or delete them
    """
    this_user = request.user
    doctors = []
    nurses = []
    admins = []
    patients = []


    if HospitalAdmin.objects.filter(pk=this_user.pk):
        admin_temp = models.HospitalAdmin.objects.get(pk=this_user.id)
        hosp = admin_temp.hptal
    for user in models.User.objects.all():
        if models.Doctor.objects.filter(pk=user.pk):
            doc_temp = models.Doctor.objects.get(pk=user.id)
            if doc_temp.hospital == hosp:
                doctors.append(user)
        elif models.Nurse.objects.filter(pk=user.pk):
            nur_temp = models.Nurse.objects.get(pk=user.id)
            if nur_temp.hospital == hosp:
                nurses.append(user)
        elif models.HospitalAdmin.objects.filter(pk=user.pk):
            admin_temp = models.HospitalAdmin.objects.get(pk=user.id)
            if admin_temp.hptal == hosp:
                admins.append(user)
        elif models.Patient.objects.filter(pk=user.pk):
            pat_temp = models.Patient.objects.get(pk=user.id)
            if pat_temp.hospital == hosp:
                patients.append(user)
    if not this_user.is_anonymous():
        user = request.user
        users = get_user_type(user)
        return render(request, 'employees.html', {'user': this_user, "admin": users[3], "patient": users[0], 'hosp': users[4],
                                             'doctor': users[1], 'nurse': users[2], 'doctors':doctors, 'nurses':nurses, 'admins':admins, 'patients':patients})
    else:
        return render_to_response('error.html')


def patients(request):
    """
        allow hospital admin to either register patients or delete them
    """
    this_user = request.user
    patients = []
    hosp = None

    if HospitalAdmin.objects.filter(pk=this_user.pk):
        admin_temp = models.HospitalAdmin.objects.get(pk=this_user.id)
        hosp = admin_temp.hptal
    for user in models.User.objects.all():
        if models.Patient.objects.filter(pk=user.pk):
            pat_temp = models.Patient.objects.get(pk=user.id)
            if pat_temp.hospital == hosp:
                patients.append(user)
    if HospitalAdmin.objects.filter(pk=request.user.id):
        user = request.user
        users = get_user_type(user)
        return render(request, 'patients.html', {'user': this_user, "admin": users[3], "patient": users[0], 'hosp': users[4],
                                             'doctor': users[1], 'nurse': users[2], 'patients':patients})
    else:
        return render_to_response('error.html')



def patient_list(request):
    """
        Displays available patient list
    """
    patients = []
    is_none = True
    this_user = request.user
    if (Doctor.objects.filter(pk=this_user.id)):
        for patient in Patient.objects.all():
            if patient.patient_doctor.username == this_user.username:
                patients.append(patient)
                is_none = False
    elif (Nurse.objects.filter(pk=this_user.id)):
        nurse = Nurse.objects.get(pk=this_user.id)
        for patient in Patient.objects.all():
            if patient.hospital == nurse.hospital:
                patients.append(patient)
                is_none = False
    if Doctor.objects.filter(pk=this_user.id) or Nurse.objects.filter(pk=this_user.id):
        users = get_user_type(this_user)
        return render(request, 'patient_list.html', {'user': this_user, "admin": users[3], "patient": users[0], 'hosp': users[4],
                                                 'doctor': users[1], 'nurse': users[2], 'patients':patients, 'is_none':is_none})
    else:
        return render_to_response('error.html')

def patient_info_emp(request, patient_id):
    """
        Displays selected patient's profile (not displaying proper top bar)
    """
    user = request.user

    if Nurse.objects.filter(pk=user.id) or Doctor.objects.filter(pk=user.id):
        patient = models.Patient.objects.get(pk=patient_id)
        enumber = patient.number_format(patient.emergency_cnumber)
        number = patient.number_format(patient.number)
        users = get_user_type(user)
        return render(request, 'patient_info_emp.html', {"user": user, "doctor":users[1], "nurse":users[2], "patient1": patient, "enumber": enumber,
                                                        "number": number})
    else:
        return render_to_response('error.html')

def change_hosp_status(request, patient_id):
    """
        Changes the patient's admission status
    """
    user = request.user

    if Nurse.objects.filter(pk=user.id) or Doctor.objects.filter(pk=user.id):
        patient = models.Patient.objects.get(pk=patient_id)
        if patient.hospital_status == patient.DISCHARGED:
            patient.hospital_status = patient.ADMITTED
            log = LogEntry(requester=patient, action="Patient Admitted: " + patient.username,
                           date=datetime.datetime.now())
            log.save()

        else:
            patient.hospital_status = patient.DISCHARGED
            log = LogEntry(requester=patient, action="Patient Discharged: " + patient.username,
                           date=datetime.datetime.now())
            log.save()
        patient.save()
        return HttpResponseRedirect(reverse('patient_info_emp', args=[int(patient_id)]))
    else:
        return render_to_response('error.html')


def med_info_edit(request, patient_id):
    """
        Allows to edit the patient's medical info (not displaying proper top bar)
    """
    user = request.user

    if Nurse.objects.filter(pk=user.id) or Doctor.objects.filter(pk=user.id):
        patient = models.Patient.objects.get(pk=patient_id)
        if request.method == "POST":
            form = forms.PatientMedForm(request.POST, instance=patient)
            if form.is_valid():
                form.save()
                log = LogEntry(requester=request.user, action="Information Update", date=datetime.datetime.now())
                log.save()
                return redirect('patient_info_emp', patient.id)

        form = forms.PatientMedForm(instance=patient)
        users = get_user_type(user)
        return render(request, 'med_info_edit.html', {'form': form, "user": user, "doctor":users[1],
                                                      "nurse":users[2], 'patient':patient})
    else:
        return render_to_response('error.html')



def createAppointment(request):
    """
            view for creating a new appointment
            :param request: the request for loading the messages page
            :return: Redirect to the 1)base calender after creating 2)form
    """

    user = request.user
    users = get_user_type(user)
    is_patient = True

    if Doctor.objects.filter(pk=request.user.id) or Patient.objects.filter(pk=request.user.id) or Nurse.objects.filter(pk=request.user.id):
        if request.method == 'POST':
            user = request.user
            form = forms.CreateAppointmentForm(request.POST)
            if form.is_valid():
                form.save()
                log = LogEntry(requester=request.user, action="Appointment Creation", date=datetime.datetime.now())
                log.save()
                return redirect('base_calendar')
        else:
            if(users[0]):   # if the user is a patient, send in the patient as the inital value
                patient = Patient.objects.get(pk=user.id)
                doctor = Doctor.objects.get(pk=patient.patient_doctor.id)
                hospital = patient.hospital_id
                form = CreateAppointmentForm(initial={'patient': patient, 'doctor': doctor})
                form.fields['doctor'].queryset = Doctor.objects.filter(hospital_id=hospital)
            elif(users[1]):           # else, send in the id of the user as the doctor
                doctor = Doctor.objects.get(pk=user.id)
                hospital = doctor.hospital_id
                form = CreateAppointmentForm(initial={'doctor': doctor})
                form.fields['patient'].queryset = Patient.objects.filter(hospital_id=hospital)
                is_patient = False
            else:
                form = CreateAppointmentForm()
                nurse = Nurse.objects.get(pk=user.id)
                hospital = nurse.hospital_id
                form.fields['patient'].queryset = Patient.objects.filter(hospital_id=hospital)
                form.fields['doctor'].queryset = Doctor.objects.filter(hospital_id=hospital)

        return render(request, 'create_appointment.html', {'form': form, 'user': user, "admin": users[3],
                                                               "patient": users[0], 'hosp': users[4], 'doctor': users[1],
                                                               'nurse': users[2], 'is_patient': is_patient })
    else:
        return render_to_response('error.html')

def updateAppointment(request, appt_id):
    """
        view for updating and appointment
        :param request: the request for updating an appointment
        :return: Redirect to the create appointment form
    """
    if Nurse.objects.filter(pk=request.user.id) or Doctor.objects.filter(pk=request.user.id) or Patient.objects.filter(
            pk=request.user.id):
        instance = get_object_or_404(Appointment, pk=appt_id)
        user = request.user

        if request.method == 'POST':
            form = forms.EditAppointmentForm(request.POST, instance=instance)
            form.doctor = instance.doctor_id
            form.patient = instance.patient_id
            if form.is_valid():
                form.save()
                form.instance.toggle_pending()

                log = LogEntry(requester=request.user, action="Appointment Update", date=datetime.datetime.now())
                log.save()
                return redirect('base_calendar')

        else:
            form = forms.EditAppointmentForm(instance=instance)

        users = get_user_type(user)
        return render(request, 'edit_appointment.html',
                      {'form': form, 'user': user, "admin": users[3], "patient": users[0], 'hosp': users[4],
                       'doctor': users[1],
                       'nurse': users[2]})
    else:
        return render_to_response('error.html')


def deleteAppointment(request, appt_id):
    """
        Deletes a given appointment from the appointment calendar
    :param request: the request to delete the appointment
    :param appt_id: the id of the appointment to be deleted
    :return: Redirect to the calendar
    """
    if Doctor.objects.filter(pk=request.user.id) or Patient.objects.filter(
            pk=request.user.id):
        delAppt = get_object_or_404(Appointment, pk=appt_id)
        delAppt.delete()
        month = datetime.date.today().month
        year = datetime.date.today().year
        return HttpResponseRedirect(reverse('calendar', args=[month, year]))
    else:
        return render_to_response('error.html')

def acceptAppointment(request, appt_id):
    """
        Accepts a given appointment from the appointment calendar
    :param request: the request to accept the appointment
    :param appt_id: the id of the appointment to be accepted
    :return: Redirect to the calendar
    """
    if Doctor.objects.filter(pk=request.user.id):
        acceptAppt = get_object_or_404(Appointment, pk=appt_id)
        acceptAppt.acceptAppointment(commit=True)
        log = LogEntry(requester=request.user, action="Appointment Accepted", date=datetime.datetime.now())
        log.save()

        month = datetime.date.today().month
        year = datetime.date.today().year
        return HttpResponseRedirect(reverse('calendar', args=[month, year]))
    else:
        return render_to_response('error.html')

def rejectAppointment(request, appt_id):
    """
        Rejects a given appointment from the appointment calendar
    :param request: the request to reject the appointment
    :param appt_id: the id of the appointment to be rejected
    :return: Redirect to the calendar
    """
    if Doctor.objects.filter(pk=request.user.id):
        rejAppt = get_object_or_404(Appointment, pk=appt_id)
        rejAppt.rejectAppointment(commit=True)
        log = LogEntry(requester=request.user, action="Appointment Rejected", date=datetime.datetime.now())
        log.save()

        month = datetime.date.today().month
        year = datetime.date.today().year
        return HttpResponseRedirect(reverse('calendar', args=[month, year]))
    else:
        return render_to_response('error.html')

def patient_edit(request):
    """
        View for editing the patient information using a specific patient edit form
        provided in the forms.py file
    :param request: request to edit a patient's profile
    :return: the patient edit form, a redirect to the patient's detail profile view if
            the submitted form is valid, or a login request if the user an an
            anonymous user
    """
    user = request.user
    if Patient.objects.filter(pk=user.id):
        patient = models.Patient.objects.get(pk=user.id)
        if request.method == "POST":
            form = forms.PatientEditForm(request.POST, instance=patient)
            if form.is_valid():
                form.save()
                log = LogEntry(requester=request.user, action="Information Update", date=datetime.datetime.now())
                log.save()
                return redirect('patient_info')
        else:
            pat = Patient.objects.get(pk=user.id)
            hosp = pat.hospital_id
            form = forms.PatientEditForm(instance=patient)
            form.fields['patient_doctor'].queryset = Doctor.objects.filter(hospital_id=hosp)
        users = get_user_type(user)
        return render(request, 'patient_edit.html', {'form': form, "user": user, "patient":users[0], "doctor":users[1],
                                                          "nurse":users[2]})
    else:
        return render_to_response('error.html')

def viewPatientPrescriptions(request, patient_id):
    """
        View for Patient, Doctor, or Nurse to see the selected Patient's list of Prescriptions
    :param request: request to view list of Patient's Prescriptions
    :param patient_id: id of the Patient who's Prescriptions you'd like to view
    :return: list of the Patient's Prescriptions
    """
    if Nurse.objects.filter(pk=request.user.id) or Doctor.objects.filter(pk=request.user.id) or Patient.objects.filter(
            pk=request.user.id):
        user = request.user
        if(models.Patient.objects.filter(pk=user.id)):
            # requesting user is the Patient
            patient = models.Patient.objects.get(pk=user.id)
            patient_prescriptions = Prescription.objects.order_by('-datePrescribed').filter(patientAssigned=patient)
            patient.prescriptions = patient_prescriptions
            user = request.user
            users = get_user_type(user)
            return render_to_response('prescriptions_list.html',
                                      {'prescriptions': patient_prescriptions, 'patient1': patient, "admin": users[3], "patient": users[0], 'hosp': users[4],
                       'doctor': users[1],
                       'nurse': users[2]})

        elif(models.Doctor.objects.filter(pk=user.id)):
            # requesting user is a Doctor
            patient = models.Patient.objects.get(pk=patient_id)
            patient_prescriptions = Prescription.objects.order_by('-datePrescribed').filter(patientAssigned=patient)
            patient.prescriptions = patient_prescriptions
            user = request.user
            users = get_user_type(user)
            return render_to_response('prescriptions_list_doctor.html',
                                      {'prescriptions': patient_prescriptions, 'patient1': patient, "admin": users[3], "patient": users[0], 'hosp': users[4],
                       'doctor': users[1],
                       'nurse': users[2]})

        elif(models.Nurse.objects.filter(pk=user.id)):
            # requesting user is a Nurse
            patient = models.Patient.objects.get(pk=patient_id)
            nurse = models.Nurse.objects.get(pk=user.id)
            if nurse.hospital == patient.hospital:
                patient_prescriptions = Prescription.objects.order_by('-datePrescribed').filter(patientAssigned=patient)
                patient.prescriptions = patient_prescriptions
                user = request.user
                users = get_user_type(user)
                return render_to_response('prescriptions_list_nurse.html',
                                          {'prescriptions': patient_prescriptions, 'patient1': patient, "admin": users[3], "patient": users[0], 'hosp': users[4],
                                            'doctor': users[1], 'nurse': users[2]})
    else:
        return render_to_response('error.html')



def newPrescription(request, patient_id):
    """
        View for Doctor to create a new Prescription for the indicated Patient.
    :param request: form to create a new Prescription
    :param patient_id: id of the Patient whom the Prescription is for
    :return: new Prescription assigned to the indicated Patient
    """
    user = request.user
    if(models.Doctor.objects.filter(pk=user.id)):
        patient = models.Patient.objects.get(pk=patient_id)
        doctor = models.Doctor.objects.get(pk=user.id)
        hospital = doctor.hospital_id
        if request.method == 'POST':
                form = forms.CreatePrescriptionForm(request.POST)

                if form.is_valid():
                    form.save()
                    log = LogEntry(requester=request.user, action="Prescription Creation: " + patient.username,
                                   date=datetime.datetime.now())
                    log.save()
                    users = get_user_type(user)
                    return redirect(reverse('prescriptions', kwargs={'patient_id': patient_id}))

        else:
            form = forms.CreatePrescriptionForm(initial={ 'doctorAssigned': doctor, 'patientAssigned': patient,
                                                          'datePrescribed': datetime.date.today() })
        user = request.user
        users = get_user_type(user)
        return render(request, 'new_prescription.html', {'form': form, 'patient1': patient, "admin": users[3], "patient": users[0], 'hosp': users[4],
                                            'doctor': users[1], 'nurse': users[2]})
    else:
        return render_to_response('error.html')

def updatePrescription(request, prescrip_id):
    """
    Generic view class for updating a Prescription
    """
    prescrip = get_object_or_404(Prescription, pk=prescrip_id)
    patient = prescrip.patientAssigned
    user = request.user
    if (models.Doctor.objects.filter(pk=user.id)):

        if request.method == 'POST':
            form = forms.EditPrescriptionForm(request.POST, instance=prescrip)
            if form.is_valid():
                form.save()
                log = LogEntry(requester=request.user, action="Prescription Update: " + patient.username, date=datetime.datetime.now())
                log.save()
                return redirect(reverse('prescriptions', kwargs={'patient_id': patient.id}))
        else:
            form = forms.EditPrescriptionForm(instance=prescrip)
        user = request.user
        users = get_user_type(user)
        return render(request, 'edit_prescription.html', {'form': form, 'user': user, 'patient1': patient, 'prescription': prescrip,
                                                          "admin": users[3],
                                                          "patient": users[0], 'hosp': users[4],
                                                          'doctor': users[1], 'nurse': users[2]
                                                          })
    else:
        return render_to_response('error.html')

def reviewPrescription(request, prescrip_id):
    """
    Generic class view for reviewing the details of a Prescription.
    ****Might not actually be used & Django just handles it****
    """
    instance = get_object_or_404(Prescription, pk=prescrip_id)
    patient = instance.patientAssigned
    user = request.user
    users = get_user_type(user)
    if (models.Doctor.objects.filter(pk=user.id)):
        return render_to_response('review_prescription_doctor.html',
                                  {'prescription': instance, 'patient1': patient, "admin": users[3],
                                   "patient": users[0], 'hosp': users[4],
                                   'doctor': users[1], 'nurse': users[2]})
    elif Nurse.objects.filter(pk=request.user.id) or Patient.objects.filter(pk=request.user.id):
        return render_to_response('review_prescription.html',
                              {'prescription': instance, 'patient1': patient, "admin": users[3],
                               "patient": users[0], 'hosp': users[4],
                               'doctor': users[1], 'nurse': users[2]})


    else:
        return render_to_response('error.html')

def deletePrescription(request, prescrip_id):
    """
    Deletes a given Prescription from the list of Prescriptions
    :param request: the request to delete the Prescription
    :param prescrip_id: the id of the Prescription to be deleted
    :return: Redirect to the list of Prescriptions
    """

    if Nurse.objects.filter(pk=request.user.id) or Doctor.objects.filter(pk=request.user.id) or Patient.objects.filter(
            pk=request.user.id):
        delPrescrip = get_object_or_404(Prescription, pk=prescrip_id)
        patient = delPrescrip.patientAssigned
        delPrescrip.delete()
        log = LogEntry(requester=request.user, action="Prescription Deletion: " + patient.username,
                       date=datetime.datetime.now())
        log.save()
        return HttpResponseRedirect(reverse('prescriptions', kwargs={'patient_id': patient.id}))
    else:
        return render_to_response('error.html')


def createTest(request):
    """
        view for creating a new test
        :param request: the request to create a new test
        :return: Redirect to the test creation form
    """
    if Doctor.objects.filter(pk=request.user.id):
        ex = 'TestDoctor'
        if request.method == 'POST':
            form = forms.CreateTestForm(request.POST)
            if form.is_valid():
                form.save()
                log = LogEntry(requester=request.user, action="Test Creation: " + form.cleaned_data['testPatient'].username,
                               date=datetime.datetime.now())
                log.save()
                return redirect('review_test')

        else:
            user = request.user
            doc = Doctor.objects.get(pk=user.id)
            doc1 = {'testDoctor': doc, 'testDate': timezone.now()}
            form = CreateTestForm(doc1)
            hosp = Doctor.objects.get(pk=user.id).hospital_id
            form.fields['testPatient'].queryset = Doctor.objects.get(pk=user.id).doctor_patients
        user = request.user
        users = get_user_type(user)
        return render(request, 'create_test.html', {'form': form, 'user': user, "admin": users[3], "patient": users[0], 'hosp':users[4], 'doctor':users[1],
                                              'nurse':users[2], 'ex':ex})
    else:
        return render_to_response('error.html')



def reviewTest(request):
    """
        Display all tests for doctor. Separated by if the test is released
        or not.
    """
    if Doctor.objects.filter(pk=request.user.id):
        user = request.user
        users = get_user_type(user)
        isEmpty = Test.objects.filter(release=False).count() == 0

        return render_to_response('list_tests.html', {
            'tests': Test.objects.all(),
            'user': user, "admin": users[3], "patient": users[0], 'hosp':users[4], 'doctor':users[1],
                                              'nurse':users[2], 'isEmpty':isEmpty
        })
    else:
        return render_to_response('error.html')


def systemStats(request, start, end):
    """
    view the system statistics
    """

    user = request.user
    users = get_user_type(user)

    return render_to_response('log.html', {
        'entries': LogEntry.objects.all(),
        'user': user, "admin": users[3], "patient": users[0], 'hosp': users[4], 'doctor': users[1],
        'nurse': users[2], 'start': start, 'end': end
    })

def timeFrameInput(request):
    """
    PView where the time frame for the System Log is inputted
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        user = request.user
        users = get_user_type(user)

        form = forms.TimeFrameFrom(request.POST)
        if form.is_valid():
            form.save()
            patientCreate = 0
            patientAdmit = 0
            patientDischarge = 0
            appointmentCreate = 0
            appointmentAccept = 0
            appointmentReject = 0
            prescriptionCreate = 0
            testCreate = 0
            patientTransfer = 0
            for e in LogEntry.objects.all():
                if e.date >= form.cleaned_data['startTime']:
                    if e.date <= form.cleaned_data['endTime']:
                        if 'Patient Account Creation' in e.action:
                            patientCreate += 1
                        elif 'Patient Admitted' in e.action:
                            patientAdmit += 1
                        elif 'Patient Discharged' in e.action:
                            patientDischarge += 1
                        elif 'Appointment Creation' in e.action:
                            appointmentCreate += 1
                        elif 'Appointment Accepted' in e.action:
                            appointmentAccept += 1
                        elif 'Appointment Rejected' in e.action:
                            appointmentReject += 1
                        elif 'Prescription Creation' in e.action:
                            prescriptionCreate += 1
                        elif 'Test Creation' in e.action:
                            testCreate += 1
                        elif 'Patient Transfer' in e.action:
                            patientTransfer += 1


            return render(request, 'log.html', {'start': form.cleaned_data['startTime'], 'end': form.cleaned_data['endTime'],
                                                'user': user, "admin": users[3], "patient": users[0], 'hosp': users[4],
                                                'doctor': users[1], 'nurse': users[2], 'entries': LogEntry.objects.all(),
                                                'createdPatients': patientCreate, 'admittedPatients': patientAdmit,
                                                'dischargedPatients': patientDischarge, 'createdApp': appointmentCreate,
                                                'acceptedApp': appointmentAccept, 'rejectedApp': appointmentReject,
                                                'prescrip': prescriptionCreate, 'test': testCreate, 'trans': patientTransfer
                                                })

        user = request.user
        users = get_user_type(user)
        return render(request, 'statsTimeInput.html',
                      {'form': form, 'user': user, "admin": users[3], "patient": users[0], 'hosp': users[4],
                       'doctor': users[1],
                       'nurse': users[2]})
    else:
        render_to_response('error.html')


def releaseTest(request, test_id):
    """
        Release an unreleased test.
        :param request: the request for releasing the test
        :param test_id: the id for the test being released
         :return: renders the page with the new released/unreleased tests
    """
    if Doctor.objects.filter(pk=request.user.id):
        Test.objects.filter(pk=test_id).update(release=True)

        user = request.user
        users = get_user_type(user)
        log = LogEntry(requester=request.user, action="Test Release", date=datetime.datetime.now())
        log.save()

        return render(request, 'list_tests.html', {
            'tests': Test.objects.all(),
            'user': user, "admin": users[3], "patient": users[0], 'hosp':users[4], 'doctor':users[1],
                                              'nurse':users[2]
        })
    else:
        return render_to_response('error.html')

def testImages(request, test_id):
    """
        View the images associated with a test.
        :param request: the request for loading the test images
        :param test_id: the id for the test's images you are trying to view
         :return: Redirect to the test images
    """
    if Doctor.objects.filter(pk=request.user.id):
        thisTest = get_object_or_404(Test, pk=test_id)
        user = request.user
        users = get_user_type(user)

        return render(request, 'test_images.html', {
            'tests': thisTest,
            'user': user, "admin": users[3], "patient": users[0], 'hosp': users[4], 'doctor': users[1],
            'nurse': users[2]
        })
    else:
        return render_to_response('error.html')

def delete_doctor(request, doctor_id):
    """
        Deletes a given doctor
    :param request: the request to delete the doctor
    :param doctor_id: the id of the doctor to be deleted
    :return: Redirect to the employee page
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        temp_doc = get_object_or_404(Doctor, pk=doctor_id)
        temp_doc.delete()
        for app in Appointment.objects.all():
            if app.doctor_id == temp_doc.id:
                app.delete()
        messages.success(request, 'doctor accounted deleted.')
        log = LogEntry(requester=request.user, action="Doctor Deletion: " + temp_doc.username,
                       date=datetime.datetime.now())
        log.save()
        return HttpResponseRedirect(reverse('employees'))
    else:
        render_to_response('error.html')

def delete_patient(request, patient_id):
    """
        Deletes a given patient
    :param request: the request to delete the patient
    :param patient_id: the id of the patient to be deleted
    :return: Redirect to the employee page
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        temp_pat = get_object_or_404(Patient, pk=patient_id)
        temp_pat.delete()
        for app in Appointment.objects.all():
            if app.patient_id == temp_pat.id:
                app.delete()
        messages.success(request, 'patient accounted deleted.')
        log = LogEntry(requester=request.user, action="Patient Deletion: " + temp_pat.username,
                       date=datetime.datetime.now())
        log.save()
        return HttpResponseRedirect(reverse('patients'))
    else:
        render_to_response('error.html')


def delete_nurse(request, nurse_id):
    """
        Deletes a given nurse
    :param request: the request to delete the nurse
    :param nurse_id: the id of the nurse to be deleted
    :return: Redirect to the employee page
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        temp_nurse = get_object_or_404(Nurse, pk=nurse_id)
        temp_nurse.delete()
        messages.success(request, 'nurse accounted deleted.')
        log = LogEntry(requester=request.user, action="Nurse Deletion: " + temp_nurse.username,
                       date=datetime.datetime.now())
        log.save()
        return HttpResponseRedirect(reverse('employees'))
    else:
        return render_to_response('error.html')

def delete_admin(request, admin_id):
    """
        Deletes a given admin
    :param request: the request to delete the admin
    :param admin_id: the id of the nurse to be deleted
    :return: Redirect to the employee page
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        temp_admin = get_object_or_404(HospitalAdmin, pk=admin_id)
        if temp_admin.id != request.user.id:
            temp_admin.delete()
            messages.success(request, 'admin accounted deleted.')
            log = LogEntry(requester=request.user, action="Admin Deletion: " + temp_admin.username,
                           date=datetime.datetime.now())
            log.save()
            return HttpResponseRedirect(reverse('employees'))

        else:
            messages.success(request, 'your account has been deleted.')
            log = LogEntry(requester=request.user, action="Admin Deletion: " + temp_admin.username,
                           date=datetime.datetime.now())
            log.save()
            logout(request)
            temp_admin.delete()
            return HttpResponseRedirect(reverse('base'))
    else:
        return render_to_response('error.html')



def test_results(request):
    """
    view for loading all tests results (for a patient)
    :param request: request for viewing test results
    :return: renders test_results.html with all the test results
    """
    if Patient.objects.filter(pk=request.user.id):
        is_none = True
        user = request.user
        users = get_user_type(user)
        tests = []
        for test in Test.objects.all():
            if test.testPatient_id == user.id and test.release:
                tests.append(test)
                is_none = False

        tests.sort(key=lambda b: b.testDate)


        return render(request, 'test_results.html', {'user': user, "admin": users[3], "patient": users[0], 'hosp': users[4],
                                             'doctor': users[1], 'nurse': users[2], 'apps': users[5], 'some': users[6], 'tests':tests, 'is_none':is_none})
    else:
        return render_to_response('error.html')





def message_new(request):
    """
        View to send a new message.
        :param request: the request for sending a new message
        :return: Redirect to the messages page
    """
    if User.objects.filter(pk=request.user.id):

        if request.method == 'POST':
            form = forms.NewMessageForm(request.POST)
            if form.is_valid():
                form.save()
                m = form.instance
                names = [(m.sender.first_name + m.sender.last_name).replace(" ", ""),
                         (m.receiver.first_name + m.receiver.last_name).replace(" ", "")]
                names.sort()
                c_id = names[0] + '-' + names[1]
                return HttpResponseRedirect(reverse('view_conversation', kwargs={'name': c_id}))
        user = request.user
        users = get_user_type(user)
        ex = 'Sender'
        ex2 = 'Created at'
        if users[0]:
            pat = Patient.objects.get(pk=user.id)
            hosp = pat.hospital_id
            pat1 = {'sender': pat, 'created_at': timezone.now()}
            form = NewMessageForm(pat1)
            form.fields['receiver'].queryset = Nurse.objects.filter(hospital_id=hosp)
        elif users[1] or users[2] or users[3]:
            if users[1]:
                doc = Doctor.objects.get(pk=user.id)
                hosp = doc.hospital_id
            elif users[2]:
                nur = Nurse.objects.get(pk=user.id)
                hosp = nur.hospital_id
            else:
                admin = HospitalAdmin.objects.get(pk=user.id)
                hosp = admin.hptal.id
            pat1 = {'sender': user, 'created_at': timezone.now()}
            form = NewMessageForm(pat1)
            unwanted = []
            if not users[2]:
                pats = Patient.objects.all()
                for pat in pats:
                    unwanted.append(pat)
            for user1 in models.User.objects.all():
                if Patient.objects.filter(pk=user1.id) and Patient.objects.get(pk=user1.id).hospital_id != hosp:
                    unwanted.append(user1)
                elif Doctor.objects.filter(pk=user1.id) and Doctor.objects.get(pk=user1.id).hospital_id != hosp:
                    unwanted.append(user1)
                elif Nurse.objects.filter(pk=user1.id) and Nurse.objects.get(pk=user1.id).hospital_id != hosp:
                    unwanted.append(user1)
                elif HospitalAdmin.objects.filter(pk=user1.id) and HospitalAdmin.objects.get(pk=user1.id).hptal_id != hosp:
                    unwanted.append(user1)
                elif user1.is_superuser:
                    unwanted.append(user1)
                unwanted.append(user)
            x_id = []
            for user in unwanted:
                x_id.append(user.id)
            q_set = models.User.objects.exclude(id__in=x_id)
            form.fields['receiver'].queryset = q_set
        else:
            form = NewMessageForm

        return render(request, 'new_message.html', {'form': form, 'user': user, "admin": users[3],
                                                               "patient": users[0], 'hosp': users[4], 'doctor': users[1],
                                                               'nurse': users[2], 'ex':ex, 'ex2':ex2})
    else:
        return render_to_response('error.html')

def message(request):
    """
           view for displaying all the conversations
           :param request: the request for loading the messages page
           :return: Redirect to the messages page

    """
    if User.objects.filter(pk=request.user.id):
        pat = None
        user = request.user
        users = get_user_type(user)
        convos = get_conv(request)
        names = convos.keys()
        is_empty = len(convos) == 0



        return render(request, 'messages.html', {'user': user, "admin": users[3], "patient": users[0], 'hosp': users[4],
                                             'doctor': users[1], 'nurse': users[2], 'apps': users[5], 'some': users[6], 'convos':convos, 'pat':pat,
                                                 'names':names, 'is_empty':is_empty})
    else:
        return render_to_response('error.html')


def get_conv(request):
    """
          returns a dictionary of conversations (conversation id -> list of messages)
          :param request: the request for loading the messages page
          :return: Redirect to the employee page
    """

    user = request.user
    users = get_user_type(user)
    convos = {}

    for m in Message.objects.all():
        if m.receiver.id == user.id or m.sender.id == user.id:
            names = [(m.sender.first_name + m.sender.last_name).replace(" ", ""), (m.receiver.first_name + m.receiver.last_name).replace(" ", "")]
            names.sort()
            c_id = names[0] + '-' + names[1]
            if c_id in convos.keys():
                convos[c_id].append(m)
            else:
                convos[c_id] = []
                convos[c_id].append(m)
    return convos

def view_conversation(request, name):
    """
           view for a given conversation
           :param request: the request to view a specific conversation
           :param name: the id for the conversation (name-name)
            :return: Redirect to the template for the conversation
    """
    if User.objects.filter(pk=request.user.id):
        user = request.user
        you = []
        other_user = None
        them = []
        user = request.user
        users = get_user_type(user)
        convos = get_conv(request)
        messages = convos[name]
        for message in messages:
            if message.sender.id == user.id:
                you.append(message)

            else:
                them.append(message)
                Message.objects.filter(pk=message.id).update(status=True)


        m = messages[0]
        if m.sender.id != user.id:
            other_user = m.sender
            other_name = m.sender.first_name + " " + m.sender.last_name

        else:
            other_user = m.receiver
            other_name = m.receiver.first_name + " " + m.receiver.last_name


        return render(request, 'view_conversation.html',
                      {'user': user, "admin": users[3], "patient": users[0], 'hosp': users[4],
                       'doctor': users[1],
                       'nurse': users[2], 'messages':messages, 'title':m, 'you':you, 'them':them, 'other_user':other_user.username, 'other_name':other_name})
    else:
        return render_to_response('error.html')

def reply(request, otheruser_name):
    """
              view for replying to a specific conversation
              :param request: the request to reply
            :param otheruser_name the user's username that you are replying to
         :return: Redirect to the view_conversation page
    """
    if User.objects.filter(pk=request.user.id):
        if request.method == 'POST':
            form = forms.NewMessageForm(request.POST)
            if form.is_valid():
                form.save()
                m = form.instance
                names = [(m.sender.first_name + m.sender.last_name).replace(" ", ""),
                         (m.receiver.first_name + m.receiver.last_name).replace(" ", "")]
                names.sort()
                c_id = names[0] + '-' + names[1]
                return HttpResponseRedirect(reverse('view_conversation', kwargs={'name': c_id}))
        user = request.user
        users = get_user_type(user)
        otheruser = models.User.objects.get(username=otheruser_name)
        ex = 'Sender'
        ex2 = 'Created at'
        ex3 = 'To'
        pat1 = {'sender': user, 'created_at': timezone.now(), 'receiver':otheruser}
        form = NewMessageForm(pat1)
        return render(request, 'new_message.html', {'form': form, 'user': user, "admin": users[3],
                                                    "patient": users[0], 'hosp': users[4], 'doctor': users[1],
                                                    'nurse': users[2], 'ex': ex, 'ex2': ex2, 'ex3':ex3, 'otheruser':otheruser})
    else:
        return render_to_response('error.html')
def export(request):
    """
    Exports the Patient's Medical Info to a CSV file (Excel Spreadsheet)
    :param request: the request to generate and download the CSV file
    :return: Downloads the CSV file
    """
    if Patient.objects.filter(pk=request.user.id):
        user = request.user
        patient = models.Patient.objects.get(pk=user.id)
        doctor = patient.patient_doctor
        doc = models.Doctor.objects.get(pk=doctor.id)


        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="MedicalInfo.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name:', patient.first_name, patient.last_name])
        writer.writerow(['Medical Info:', patient.medical_history])
        writer.writerow(['Insurance Info:', patient.insurance_information])
        writer.writerow(['Hospital:', patient.hospital])
        writer.writerow(['Doctor:', doc.first_name, doc.last_name])
        writer.writerow([])

        test_count = 0
        for test in Test.objects.all():
            if test.testPatient == patient:
                test_count += 1
                writer.writerow(['Test #', test_count])
                writer.writerow(['Test Name:', test.name])
                writer.writerow(['Test Date:', test.testDate])
                writer.writerow(['Test Doctor:', test.testDoctor])
                writer.writerow(['Test Results:', test.results])
                writer.writerow([])
        if test_count == 0:
            writer.writerow(['Tests:', 'None'])
            writer.writerow([])

        prescrip_count = 0
        for prescrip in Prescription.objects.all():
            if prescrip.patientAssigned == patient:
                prescrip_count += 1
                writer.writerow(['Prescription #', prescrip_count])
                writer.writerow(['Prescription Name:', prescrip.prescription_name])
                writer.writerow(['Date Prescribed:', prescrip.datePrescribed])
                writer.writerow(['Doctor:', prescrip.doctorAssigned])
                writer.writerow(['Description:', prescrip.description])
                writer.writerow([])
        if prescrip_count == 0:
            writer.writerow(['Prescriptions:', 'None'])

        return response
    else:
        return render_to_response('error.html')


def newTransferRequest(request):
    """
        View for a Doctor or Hospital Admin to request to transfer a patient to another hospital.
        Gathers the inital information of the patient to transfer and the hospital to transfer him
        to
    :param request: form to create a new TransferRequest
    :return: rendering of form
    """
    if HospitalAdmin.objects.filter(pk=request.user.id) or Doctor.objects.filter(pk=request.user.id):

        user = request.user
        users = get_user_type(user)

        if request.method == 'POST':
            # create a form instance and populate it with data
            firstForm = forms.TransferRequestPatientHospitalForm(request.POST)

            if firstForm.is_valid():
                patient = firstForm.cleaned_data['patient_to_transfer'].id
                hospital = firstForm.cleaned_data['receiving_hospital'].id

                return HttpResponseRedirect(reverse('complete_transfer_request', args=[patient, hospital]))

        else:

            # create a form instance and populate it with data
            firstForm = forms.TransferRequestPatientHospitalForm()

            initial_hospital = None                             # the hospital that the user is in
            if HospitalAdmin.objects.filter(pk=user.id):        # get the hospital of the user
                admin = HospitalAdmin.objects.get(pk=user.id)
                initial_hospital = admin.hptal
            elif Doctor.objects.filter(pk=user.id):
                doc = Doctor.objects.get(pk=user.id)
                initial_hospital = doc.hospital

            firstForm.fields['patient_to_transfer'].queryset = Patient.objects.filter(hospital__id=initial_hospital.id)
            firstForm.fields['receiving_hospital'].queryset = Hospital.objects.exclude( id=initial_hospital.id )

        return render(request, 'transferRequestForm.html', {'form': firstForm, 'user': user, "admin": users[3],
                                                            "patient": users[0], 'hosp': users[4], 'doctor': users[1],
                                                            'nurse': users[2], 'is_second': False})
    else:
        return render_to_response('error.html')

def newTransferRequestComplete(request, patient, hospital):
    """
        Completes and saves a transfer request with the given information and
        the information collected from a second form that will grab the
        new doctor to assign to the patient and the admin to send the request
    :param request: POST or GET
    :param patient: the id of the patient that will be transferred
    :param hospital: the id of the hospital that the patient will be transfered to
    :return: redirect to a form or the patients list of form is valid
    """

    user = request.user
    users = get_user_type(user)
    requestor = request.user

    if HospitalAdmin.objects.filter(pk=request.user.id) or Doctor.objects.filter(pk=request.user.id):
        if request.method == 'POST':
            form = forms.TransferRequestDoctorAdminForm(request.POST)

            if form.is_valid():

                # if the form is valid, create a new transfer request with the given information
                transferRequest = TransferRequest()
                transferRequest.patient_to_transfer = Patient.objects.get(pk=patient)     # get the patient to transfer
                transferRequest.receiving_hospital = Hospital.objects.get(pk=hospital)    # get the receiving hospital
                transferRequest.new_doctor = form.cleaned_data['new_doctor']              # get the new doctor
                transferRequest.receiving_admin = form.cleaned_data['receiving_admin']    # get the receiving administrator
                transferRequest.requester = requestor
                transferRequest.save()

                # create a transfer request reply that will alert the sender to the outcome of the transfer request
                response = TransferRequestReply(acceptance_reply=TransferRequestReply.PENDING, receiver=requestor,
                                                transfer_request=transferRequest)
                response.save()

                # redirecting to either the doctor or admin patient page
                if HospitalAdmin.objects.filter(pk=user.id):
                    return redirect(reverse('patients'))
                elif Doctor.objects.filter(pk=user.id):
                    return redirect(reverse('patient_list'))
                else:
                    return render_to_response('error.html')

        else:
            form = forms.TransferRequestDoctorAdminForm()

            # filter the fields so that only doctors and admins from the same hospital appear
            form.fields['new_doctor'].queryset = Doctor.objects.filter( hospital__id=hospital )
            form.fields['receiving_admin'].queryset = HospitalAdmin.objects.filter( hptal__id=hospital )

        return render(request, 'transferRequestForm.html', {'form': form, 'user': user, "admin": users[3],
                                                            "patient": users[0], 'hosp': users[4], 'doctor': users[1],
                                                            'nurse': users[2], 'is_second': True})
    else:
        return render_to_response('error.html')

def deleteRequest(request, req_id):
    """
        Deletes a given appointment from the appointment calendar
    :param request: the request to delete the appointment
    :param appt_id: the id of the appointment to be deleted
    :return: Redirect to the calendar
    """
    if HospitalAdmin.objects.filter(pk=request.user.id) or Doctor.objects.filter(pk=request.user.id):
        delReq = get_object_or_404(TransferRequest, pk=req_id)
        delTransResponse = models.TransferRequestReply.objects.filter(
            transfer_request__id=delReq.id,
        )

        delReq.delete()
        delTransResponse.delete()
        return HttpResponseRedirect(reverse('base'))
    else:
        return render_to_response('error.html')

def acceptRequest(request, req_id):
    """
        Accepts a given transfer request
    :param request: the request to accept the transfer
    :param req_id: the transfer request id
    :return: redirect to the base page
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        # get the request object
        acceptReq = get_object_or_404(TransferRequest, pk=req_id)

        # generate a transfer request reply to alert the sending party that the request has been accepted
        transfer_response = models.TransferRequestReply.objects.get(transfer_request__id=req_id,)
        transfer_response.acceptance_reply = TransferRequestReply.ACCEPTED
        transfer_response.save()
        log = LogEntry(requester=request.user, action="Patient Transfer: " + acceptReq.patient_to_transfer.username,
                       date=datetime.datetime.now())
        log.save()

        # perform the operations necessary to actually accept the request
        acceptReq.accept_request()

        return HttpResponseRedirect(reverse('base'))
    else:
        return render_to_response('error.html')

def rejectRequest(request, req_id):
    """
        Rejects a given transfer request
    :param request: the request to reject the transfer
    :param req_id: the id of the transfer request
    :return: redirect to the base page
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        # generate a transfer request reply to alert the sending party that the request has been accepted
        transfer_request = get_object_or_404(TransferRequest, pk=req_id)
        transfer_request.reject_request()

        return HttpResponseRedirect(reverse('base'))
    else:
        return render_to_response('error.html')


def rejectRequestForm(request, req_id):
    """
        Has user fill out a form explaining why the request was rejected
    :param request:
    :param req_id:
    :return:
    """
    if HospitalAdmin.objects.filter(pk=request.user.id):
        user = request.user
        users = get_user_type(user)

        transfer_request = get_object_or_404(TransferRequest, pk=req_id)
        transfer_response = models.TransferRequestReply.objects.get(transfer_request__id=req_id, )

        if request.method == 'POST':
            form = forms.RejectTransferRequestForm(request.POST, instance=transfer_response )
            if form.is_valid():
                form.save()
                transfer_request.reject_request()
                return redirect(reverse('base'))
        else:
            form = forms.RejectTransferRequestForm(instance=transfer_response)

        return render(request, 'transferRequestReplyForm.html', {'form': form, 'user': user, "admin": users[3],
                                                               "patient": users[0], 'hosp': users[4], 'doctor': users[1],
                                                               'nurse': users[2],})
    else:
        return render_to_response('error.html')