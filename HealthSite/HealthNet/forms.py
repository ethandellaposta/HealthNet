"""
    File containing the creation and edit forms for Patients and Appointments

    @authors: Theodora Bendlin, Ethan Della Posta, Laura Corrigan, Benjamin Kirby, Eliott Frilet
"""
from datetime import datetime, timedelta
from django.utils import timezone

from django import forms
from django.contrib.auth import authenticate
from django.forms import Textarea
from django.forms import ValidationError

from .models import Doctor, HospitalAdmin
from . import models
from itertools import chain

class PatientForm(forms.ModelForm):
    """
        Form for creating a patient
    """
    class Meta:
        model = models.Patient
        fields = ['first_name', 'last_name', 'username', 'password', 'confirm_password', 'email', 'medical_history', 'known_allergies',
                  'current_medications', 'medical_conditions', 'insurance_information',
                  'street', 'city', 'state', 'country', 'zip', 'emergency_cname', 'emergency_cnumber',
                 'number','hospital', 'patient_doctor',]

        widgets = {
            'medical_history': forms.Textarea(attrs={'style': 'width: 375px; height: 175px; resize:none'}),
            'known_allergies': forms.Textarea(attrs={'style': 'width: 375px; height: 175px; resize:none'}),
            'current_medications': forms.Textarea(attrs={'style': 'width: 375px; height: 175px; resize:none'}),
            'medical_conditions': forms.Textarea(attrs={'style': 'width: 375px; height: 175px; resize:none'}),
            'password': forms.PasswordInput(),
            'confirm_password': forms.PasswordInput()

        }

        help_texts = {'username': None, 'patient_doctor': 'Doctor must be from your chosen hospital.',}


    def clean(self):
        cleaned_data = super(PatientForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )


    def is_valid(self):
        """
            Validation form for patients
        :return:
        """
        valid = super(PatientForm, self).is_valid()
        if valid:
            doc = self.cleaned_data.get('patient_doctor')

            hos = self.cleaned_data.get('hospital')

            if doc.hospital_id == hos.id:
                return True
            else:
                return False
        else:
            return False



    def save(self, commit=True):
        """
            Save function for saving an instance of a patient
        :return: Created instance of a patient
        """
        instance = super(PatientForm, self).save(commit=False)
        instance.username = self.cleaned_data['username']
        instance.set_password(raw_password=self.cleaned_data['password'])
        if commit:
            instance.save()
        return instance

class DoctorForm(forms.ModelForm):
    """
        Form for creating a patient
    """
    class Meta:
        model = models.Doctor
        fields = ['first_name', 'last_name', 'gender', 'username', 'password', 'confirm_password', 'hospital']
        help_texts = {'username': None,}
        widgets = {
            'password': forms.PasswordInput(),
            'confirm_password': forms.PasswordInput()
        }


    def save(self, commit=True):
        """
            Save function for saving an instance of a patient
        :return: Created instance of a patient
        """
        instance = super(DoctorForm, self).save(commit=False)
        instance.username = self.cleaned_data['username']
        instance.set_password(raw_password=self.cleaned_data['password'])
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super(DoctorForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )


class NewMessageForm(forms.ModelForm):
    """
        Form for sending a message
    """
    class Meta:
        model = models.Message
        fields = ['sender', 'receiver', 'msg_content', 'created_at']
        widgets = {'msg_content': Textarea(attrs={'style':'resize:none'}),
                   }
    def save(self, commit=True):
        """
            Save function for saving the message
        """
        instance = super(NewMessageForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance



class NurseForm(forms.ModelForm):
    """
        Form for creating a patient
    """
    class Meta:
        model = models.Nurse
        fields = ['first_name', 'last_name', 'gender', 'username', 'password', 'confirm_password', 'hospital']
        help_texts = {'username': None,}
        widgets = {
            'password': forms.PasswordInput(),
            'confirm_password': forms.PasswordInput()
        }


    def save(self, commit=True):
        """
            Save function for saving an instance of a patient
        :return: Created instance of a patient
        """
        instance = super(NurseForm, self).save(commit=False)
        instance.username = self.cleaned_data['username']
        instance.set_password(raw_password=self.cleaned_data['password'])
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super(NurseForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )


class HNAdminForm(forms.ModelForm):
    """
        Form for creating a hospital admin from HealthNet
    """
    class Meta:
        model = models.HospitalAdmin
        fields = ['first_name', 'last_name', 'gender', 'username', 'password', 'confirm_password', 'hptal']
        help_texts = {'username': None,}
        widgets = {
            'password': forms.PasswordInput(),
            'confirm_password': forms.PasswordInput()
        }


    def save(self, commit=True):
        """
            Save function for saving an instance of a patient
        :return: Created instance of a patient
        """
        instance = super(HNAdminForm, self).save(commit=False)
        instance.username = self.cleaned_data['username']
        instance.set_password(raw_password=self.cleaned_data['password'])
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super(HNAdminForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )



class PatientEditForm(forms.ModelForm):
    """
        Edit form for editing the available fields for a patient
    """
    class Meta:
        model = models.Patient
        fields = ['first_name', 'last_name', 'email', 'insurance_information',
                  'street', 'city', 'state', 'country', 'zip', 'emergency_cname', 'emergency_cnumber',
                 'patient_doctor','number']

class PatientMedForm(forms.ModelForm):
    """
        Edit form for editing the medical history of a patient
    """
    class Meta:
        model = models.Patient
        fields = ['medical_history', 'known_allergies', 'current_medications', 'medical_conditions']
        widgets = {
            'medical_history': forms.Textarea(attrs={'style': 'width: 375px; height: 175px; resize:none'}),
            'known_allergies': forms.Textarea(attrs={'style': 'width: 375px; height: 175px; resize:none'}),
            'current_medications': forms.Textarea(attrs={'style': 'width: 375px; height: 175px; resize:none'}),
            'medical_conditions': forms.Textarea(attrs={'style': 'width: 375px; height: 175px; resize:none'}),

        }

class LoginForm(forms.Form):
    """
        Login form that will take in a username and password and attempt
        to log the patient into Healthnet
    """
    class Meta:
        username = forms.CharField(widget=forms.TextInput())
        password = forms.CharField(widget=forms.TextInput())
        model = models.Patient
        fields = ['username', 'password']

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("This user does not exist")
        if not user.check_password(password):
            raise forms.ValidationError("Incorrect password")
        if not user.is_active:
            raise forms.ValidationError("This user is no longer active")
        return super(LoginForm, self).clean()

class CreateAppointmentForm(forms.ModelForm):
    """
        Creation form for an appointment
    """

    class Meta:
        model = models.Appointment
        fields = ['appointment_time', 'reason', 'doctor', 'patient']
        widgets = {
            'appointment_time': forms.DateTimeInput(attrs={'class': 'datetime-input'}),
            'reason': forms.Textarea(attrs={'style': 'height: 50px; width: 300px;'})
        }
        help_texts = {'appointment_time': 'Format: YYYY-MM-DD   HH:MM:SS (military time)'}

    def save(self, commit=True):
        """
            Save function for saving the created instance of an appointment
        :return the created Appointment object
        """
        instance = super(CreateAppointmentForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance

    def is_valid(self):
        """
            Validation function for an appointment associated form
        :return: true if the form is valid, false otherwise
        """

        # use the super's validation form to check base functionality
        valid = super(CreateAppointmentForm, self).is_valid()

        if not valid:
            return valid

        else:
            return self.check_datetime()

    def check_datetime(self):
        """
            Checks to see if the date and time for the appointment is
            appropriate
            1. The doctor doesn't have another appointment at the same
            time
            2. The doctor doesn't have another appointment within a half
            hour of this appointment
            3. The patient doesn't have another appointment at the same
            time as this appointment
            4. The patient doesn't have another appointment within a half
            hour of this appointment
            5. The appointment is being made in the past
        :return: true if the appointment has the same doctor and time,
                false otherwise
        """

        # first, check to make sure that the time isn't in the past
        time = self.cleaned_data['appointment_time'] # this appointments time
        if time <= timezone.now():
            self.add_error('appointment_time', ValidationError(message='Entered time is in the past', code='invalid'))
            return False

        # try to get an appointment with the same datetime and doctor
        try:
            appointment = models.Appointment.objects.get(
                appointment_time=time,
                doctor=self.cleaned_data['doctor'].id
            )
            self.add_error('appointment_time', ValidationError(message='The doctor already has an appointment at this time. Please choose another.', code='invalid'))
            return False # if it exists, return false

        except models.Appointment.MultipleObjectsReturned:
            self.add_error('appointment_time', ValidationError(
                message='The doctor is not available at this time. Please choose another time.', code='invalid'))
            return False    # sanity check; possible exception raised when
                            # using get(), and should return false

        # if there is not an appointment with the same date and time,
        # then check to see if the doctor has another appointment with
        # another patient at around this date and time
        except models.Appointment.DoesNotExist:

            try:
                appointments = models.Appointment.objects.filter(
                    appointment_time__day=time.day,
                    doctor=self.cleaned_data['doctor'].id
                )

                for appt in appointments:

                    # check to see if times are within a half hour of each other
                    if self.is_within_halfhour(appt):
                        self.add_error('appointment_time',
                                       ValidationError(message='The doctor is not available at this time. Please choose another time', code='invalid'))
                        return False


            except models.Appointment.DoesNotExist:
                pass

        # attempt to see if this patient has another appointment at the
        # same date and time
        try:
            appointment = models.Appointment.objects.get(
                appointment_time=time,
                patient=self.cleaned_data['patient'].id
            )
            self.add_error('appointment_time', ValidationError(
                message='The patient already has an appointment at this time. Please choose another time.', code='invalid'))
            return False # if it exists, return false

        except models.Appointment.MultipleObjectsReturned:
            self.add_error('appointment_time', ValidationError(
                message='The patient already have an appointment at this time. Please choose another time.', code='invalid'))
            return False    # sanity check; possible exception raised when
                            # using get(), and should return false

        # if there is not an appointment with the same date and time,
        # then check to see if the patient has another appointment with
        # a doctor at around this date and time
        except models.Appointment.DoesNotExist:

            try:
                appointments = models.Appointment.objects.filter(
                    appointment_time__day=time.day,
                    patient=self.cleaned_data['patient'].id
                )


                for appt in appointments:

                    # check to see if times are within a half hour of each other
                    if self.is_within_halfhour(appt):
                        self.add_error('appointment_time',
                                       ValidationError(message='The patient has an appointment within half an hour of this time. '
                                                               'Please choose another time', code='invalid'))
                        return False

            except models.Appointment.DoesNotExist:
                pass

        # if all tests are passed, then return true
        return True

    def is_within_halfhour(self, appt):
        """
            Helper function that determines if the given appointment is within
            half an hour of the appointment associated with this form
        :param appt: the other appointment
        :return: true if the times are <= 30 minutes, false otherwise
        """

        time = self.cleaned_data['appointment_time'] # this appointments time
        otherTime = appt.appointment_time

        hourDiff = time.hour - otherTime.hour
        if abs(hourDiff) <= 1:    # times aren't conflicting if the hour is off by 2+
            minuteDiff = time.minute - otherTime.minute
            if abs(minuteDiff) < 30:                      # need to check the time
                # if the times are within different hours and the minute is 45, then
                # they are fine
                if(abs(hourDiff) == 1) and (time.minute == 15 or otherTime.minute == 15):
                    return False
                else:       # otherwise, the times are not fine
                    return True
        else:
            return False


class EditAppointmentForm(forms.ModelForm):
    """
        Edit form for an appointment
    """
    class Meta:
        model = models.Appointment
        fields = [ 'reason', 'appointment_time', 'doctor', 'patient']
        widgets = {
            'appointment_time': forms.DateTimeInput(attrs={'class': 'datetime-input'}),
            'reason': forms.Textarea(attrs={'style': 'height: 50px; width: 300px;'}),
            'doctor': forms.HiddenInput(),
            'patient': forms.HiddenInput()
        }
        help_texts = {'appointment_time': 'Format: YYYY-MM-DD   HH:MM:SS (military time)'}

    def is_valid(self):
        """
            Validation function for an appointment associated form
        :return: true if the form is valid, false otherwise
        """

        # use the super's validation form to check base functionality
        valid = super(EditAppointmentForm, self).is_valid()

        if not valid:
            return valid

        else:
            return self.check_datetime()

    def check_datetime(self):
        """
            Checks to see if the date and time for the appointment is
            appropriate
            1. The doctor doesn't have another appointment at the same
            time
            2. The doctor doesn't have another appointment within a half
            hour of this appointment
            3. The patient doesn't have another appointment at the same
            time as this appointment
            4. The patient doesn't have another appointment within a half
            hour of this appointment
            5. The appointment is being made in the past
        :return: true if the appointment has the same doctor and time,
                false otherwise
        """

        # first, check to make sure that the time isn't in the past
        time = self.cleaned_data['appointment_time'] # this appointments time
        if time <= timezone.now():
            self.add_error('appointment_time', ValidationError(message='Entered time is in the past', code='invalid'))
            return False

        # try to get an appointment with the same datetime and doctor
        try:
            appointment = models.Appointment.objects.get(
                appointment_time=time,
                doctor=self.cleaned_data['doctor'].id
            )
            if(appointment.id != self.instance.id):
                self.add_error('appointment_time', ValidationError(message='The doctor already has an appointment at this time. Please choose another.', code='invalid'))
                return False # if it exists, return false

        except models.Appointment.MultipleObjectsReturned:
            self.add_error('appointment_time', ValidationError(
                message='The doctor is not available at this time. Please choose another time.', code='invalid'))
            return False    # sanity check; possible exception raised when
                            # using get(), and should return false

        # if there is not an appointment with the same date and time,
        # then check to see if the doctor has another appointment with
        # another patient at around this date and time
        except models.Appointment.DoesNotExist:

            try:
                appointments = models.Appointment.objects.filter(
                    appointment_time__day=time.day,
                    doctor=self.cleaned_data['doctor'].id
                )

                for appt in appointments:

                    if (appt.id != self.instance.id):
                        currTime = appt.appointment_time

                        # check to see if times are within a half hour of each other
                        if self.is_within_halfhour(appt):
                            self.add_error('appointment_time',
                                           ValidationError(message='The doctor is not available at this time. Please choose another time', code='invalid'))
                            return False


            except models.Appointment.DoesNotExist:
                pass

        # attempt to see if this patient has another appointment at the
        # same date and time
        try:
            appointment = models.Appointment.objects.get(
                appointment_time=time,
                patient=self.cleaned_data['patient'].id
            )
            if (appointment.id != self.instance.id):
                self.add_error('appointment_time', ValidationError(
                    message='You already have an appointment at this time. Please choose another time.', code='invalid'))
                return False # if it exists, return false

        except models.Appointment.MultipleObjectsReturned:
            self.add_error('appointment_time', ValidationError(
                message='You already have an appointment at this time. Please choose another time.', code='invalid'))
            return False    # sanity check; possible exception raised when
                            # using get(), and should return false

        # if there is not an appointment with the same date and time,
        # then check to see if the patient has another appointment with
        # a doctor at around this date and time
        except models.Appointment.DoesNotExist:

            try:
                appointments = models.Appointment.objects.filter(
                    appointment_time__day=time.day,
                    patient=self.cleaned_data['patient'].id
                )


                for appt in appointments:
                    if (appt.id != self.instance.id):

                        # check to see if times are within a half hour of each other
                        if self.is_within_halfhour(appt):
                            self.add_error('appointment_time',
                                           ValidationError(message='You have an appointment within half an hour of this time. '
                                                                   'Please choose another time', code='invalid'))
                            return False

            except models.Appointment.DoesNotExist:
                pass

        # if all tests are passed, then return true
        return True

    def is_within_halfhour(self, appt):
        """
            Helper function that determines if the given appointment is within
            half an hour of the appointment associated with this form
        :param appt: the other appointment
        :return: true if the times are <= 30 minutes, false otherwise
        """

        time = self.cleaned_data['appointment_time'] # this appointments time
        otherTime = appt.appointment_time

        hourDiff = time.hour - otherTime.hour
        if abs(hourDiff) <= 1:    # times aren't conflicting if the hour is off by 2+
            minuteDiff = time.minute - otherTime.minute
            if abs(minuteDiff) < 30:                      # need to check the time
                # if the times are within different hours and the minute is 45, then
                # they are fine
                if(abs(hourDiff) == 1) and (time.minute == 15 or otherTime.minute == 15):
                    return False
                else:       # otherwise, the times are not fine
                    return True
        else:
            return False

class HospitalAdminForm(forms.ModelForm):
    model = models.HospitalAdmin
    fields = ['username', 'password', 'email']

    def save(self, commit=True):
        """
            Save function for saving an instance of a patient
        :return: Created instance of a patient
        """
        instance = super(HospitalAdminForm, self).save(commit=False)
        instance.username = self.cleaned_data['username']
        instance.set_password(raw_password=self.cleaned_data['password'])
        if commit:
            instance.save()
        return instance


class CreateTestForm(forms.ModelForm):
    """
        Creation form for a test
    """

    class Meta:
        model = models.Test
        fields = ['name', 'results', 'release', 'testDate', 'testDoctor', 'testPatient']
        widgets = {
            'testDate': forms.DateTimeInput(attrs={'class': 'testdate'})
        }
    def save(self, commit=True):
        """
            Save function for saving the created instance of a test
        :return the created Test object
        """
        instance = super(CreateTestForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance


class TimeFrameFrom(forms.ModelForm):
    """
    Form to input time frame for viewing system log
    """
    class Meta:
        model = models.TimeFrame
        fields = {'startTime', 'endTime'}


class Log(forms.ModelForm):
    """
    form for the system log
    """
    class Meta:
        model = models.LogEntry
        fields = {'requester', 'action', 'date'}


class CreatePrescriptionForm(forms.ModelForm):
    """
    Creation form for a Prescription.
    """
    class Meta:
        model = models.Prescription
        fields = {'prescription_name', 'description', 'patientAssigned', 'doctorAssigned', 'datePrescribed'}
        widgets = {'datePrescribed': forms.DateInput(attrs={'class': 'date-input'}),
                   'description': forms.Textarea(attrs={'style': 'height: 50px; width: 300px;'}),
                    'doctorAssigned': forms.HiddenInput(), 'patientAssigned': forms.HiddenInput(),
                   'datePrescribed': forms.HiddenInput()}

    def save(self, commit=True):
        """
        Save function for saving the created instance of a Prescription
        :return: the created Prescription object
        """
        instance = super(CreatePrescriptionForm, self).save(commit=False)
        if commit:
            instance.save()
            patient = instance.patientAssigned

            patient.hospital.prescriptionMasterList.append(self)   # add the new Prescription to the Master List
        return instance

class EditPrescriptionForm(forms.ModelForm):
    """
    Edit form for a Prescription
    """
    class Meta:
        model = models.Prescription
        fields = ['prescription_name', 'description', 'datePrescribed']
        widgets = {'datePrescribed': forms.HiddenInput(), 'description': forms.Textarea(attrs={'style': 'height: 50px; width: 300px;'}),}

class RejectTransferRequestForm(forms.ModelForm):
    """
        Simple form containing the optional reason field for a
        Transfer request reply
    """

    class Meta:

        model = models.TransferRequestReply
        fields = ['reason']

class TransferRequestPatientHospitalForm(forms.Form):
    """
        Form for grabbing the patient to transfer and
        the hospital to transfer him to for a transfer request
    """
    # the patient to transfer to a different hospital
    patient_to_transfer = forms.ModelChoiceField(queryset=models.Patient.objects.all())

    # the choice to transfer to a different hospital
    receiving_hospital = forms.ModelChoiceField(queryset=models.Hospital.objects.all())

    fields = ['patient_to_transfer', 'receiving_hospital']

    def is_valid(self):
        """
            Validation function that verifies the form. Additional requirements
            is that the patient is not from the same hospital as the one
            that is being chosen
        :return:
        """
        # use the super's validation form to check base functionality
        valid = super(TransferRequestPatientHospitalForm, self).is_valid()

        if not valid:
            return valid
        else:
            if self.cleaned_data['patient_to_transfer'].id != self.cleaned_data['receiving_hospital'].id:
                return True
            else:
                self.add_error('receiving_hospital',
                               ValidationError(
                                   message='The hospital cannot be the same as the patient\'s hospital',
                                   code='invalid'))
                return False

class TransferRequestDoctorAdminForm(forms.Form):
    """
        form for grabbing the new doctor and receiving admin
        for a transfer request
    """

    # the new doctor to assign the patient to
    new_doctor = forms.ModelChoiceField(queryset=models.Doctor.objects.all())

    # the admin to send the transfer request to
    receiving_admin = forms.ModelChoiceField(queryset=models.HospitalAdmin.objects.all())

    fields = ['new_doctor', 'receiving_admin']