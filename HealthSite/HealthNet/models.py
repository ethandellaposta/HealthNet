"""
   File contains all necessary models for the current implementation of HealthNet:
    Patient
    Doctor
    Nurse
    Appointment
    ApptCalendar
    Hospital
    Prescription
    HospitalAdmin

    @authors: Laura Corrigan, Benjamin Kirby, Ethan Della Posta, Theodora Bendlin
"""

from __future__ import unicode_literals

import django
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_init
from datetime import date
from itertools import groupby
from django.core.urlresolvers import reverse



class Patient(User):
    """
        Model for a patient that inherits from the User class and then provides
        other necessary fields for the patient's profile
    """

    ### FIELDS ###

    ADMITTED = 'Admitted'
    DISCHARGED = 'Not Admitted'

    HOSPITAL_STATUS_CHOICES = (
        (ADMITTED, 'Admitted'),
        (DISCHARGED, 'Not Admitted'),
    )

    conversations = {}

    """So that patients can be assigned to hospital (reverse relation)"""
    hospital = models.ForeignKey('Hospital', related_name='hospital_patients')

    """confirm a password"""
    confirm_password = models.CharField(max_length=20, default="")

    """So that patients can be assigned to doctors (reverse relation)"""
    patient_doctor = models.ForeignKey('Doctor', related_name='doctor_patients', verbose_name='Primary Doctor')

    """The current user associated with the patient"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    """The medical history of the patient"""
    medical_history = models.CharField(max_length=250)

    """The known allergies of the patient"""
    known_allergies = models.CharField(max_length=250, default="")

    """The current medication of the patient"""
    current_medications = models.CharField(max_length=250, default="")

    """The medical conditions that the patient has"""
    medical_conditions = models.CharField(max_length=250, default="")

    """The patient's insurance information"""
    insurance_information = models.CharField(max_length=250, default="None")

    """Fields relating to the address of the patient"""
    street = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    zip = models.CharField(max_length=30)

    """The patient's emergency contact information"""
    emergency_cname = models.CharField(max_length=30, verbose_name='Emergency Contact Name')
    emergency_cnumber = models.CharField(max_length=10, verbose_name='Emergency Contact Number')

    """The patient's contact number"""
    number = models.CharField(max_length=10, verbose_name="Your Phone Number")

    """Status reguarding whether or not the patient is admitted to a hospital"""
    hospital_status = models.SlugField(max_length=50, choices=HOSPITAL_STATUS_CHOICES, default=DISCHARGED,)

    """List of Patient's Prescriptions"""
    prescriptions = []



    ### FUNCTIONS ####

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def init_patient(self, usern, pw):
        """
            Initializes a patient to have the given username and password
        :param usern: (str) the patient's username
        :param pw: (str) the patient's password
        :return: (Patient) the new instance of the Patient object
        """
        patient = self.__init__(self, usern, pw)
        return patient

    def export_medical_info(self):
        """
            Function that will export a patient's medical information to another
            hospital
        :return:
        """
        pass

    def get_hospital_status(self):
        """
            Returns the admission status of the patient
        :return: (str) the admission status of the patient
        """
        return self._hospital_status

    def get_results(self):
        """
            Getter function that will get the patient's test results when implemented
        :return:
        """
        pass

    def number_format(self, number):
        """
            Helper function that correctly formats a telephone number
        :param number: (str) the unformatted telephone number
        :return: the correct string representation of the telephone number
        """
        return '(' + number[:3] + ') ' + number[3:6] +'-'+ number[6:]

    class Meta:
        """
            Changes the name of model from User to Patient in Django Admin console
        """
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'


class Nurse(User):
    """
        Dummy nurse class created for testing purposes
    """

    ### FIELDS ###
    """confirm a password"""
    confirm_password = models.CharField(max_length=20, default="")

    """The user associated with the Nurse instance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    MALE = 'M'
    FEMALE = 'F'
    GENDER = (
        (MALE, "Male"),
        (FEMALE, "Female"))

    gender = models.CharField(max_length=1, null=True, choices=GENDER,
                              verbose_name='Gender')
    hospital = models.ForeignKey('Hospital', related_name='nurses')

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    class Meta:
        """
            Changes the name of model from User to Nurse in Django Admin console
        """
        verbose_name = 'Nurse'
        verbose_name_plural = 'Nurses'


class Doctor(User):
    """
       Doctor class

    """
    """confirm a password"""
    confirm_password = models.CharField(max_length=20, default="")

    ### FIELDS ###


    """The user associated with the doctor instance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey('Hospital', related_name='doctors')
    MALE = 'M'
    FEMALE = 'F'
    GENDER = (
        (MALE, "Male"),
        (FEMALE, "Female"))

    gender = models.CharField(max_length=1, null=True, choices=GENDER,
                            verbose_name='Gender')

    def __str__(self):
        return 'Dr. ' + self.first_name + ' ' + self.last_name

    class Meta:
        """
            Changes the name of the model from User to Doctor in Django Admin Console
        """
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'


class Appointment(models.Model):
    """
        Class representing a patient appointment. Upon initialization,
        the status of the Appointment is pending, and will change when the
        associated doctor chooses to accept/reject the appointment
    """

    ### CONSTANTS ###

    # These are the constants for the accept state choices
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    PENDING = 'Pending'


    ### FIELDS ###
    # The date and time of the appointment
    appointment_time = models.DateTimeField('Appointment Time', default=timezone.now, )

    # Status of the Appointment -- Accepted, rejected or pending
    accept_state = models.SlugField(max_length=10, default="Pending")

    # Reason for the appointment
    reason = models.CharField(max_length=250)

    # The doctor associated with the appointment
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='Doctor',)

    # The patient associated with the appointment
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='Patient',)

    def modify_appointment(self, doctor, date_time, reason):
        """
            Modifies the editable appointment information with the
            given values
        :param doctor:    The updated doctor
        :param date_time: The updated Date/Time
        :param reason:    The updated reason
        :return:
        """
        self.doctor = doctor
        self.date_time = date_time
        self.reason = reason
        self.accept_state = Appointment.PENDING

    def timeToString(self):
        """
            Converts the appointment time to normal American time format
        :return: str representing the appointment time
        """
        time = self.appointment_time
        strTime = time.strftime("%H:%M").split(":")

        hour = int(strTime[0])
        suffix = "am"
        if(hour > 12):
            hour = hour - 12
            suffix = "pm"

        return str(hour) + ":" + strTime[1] + suffix

    def acceptAppointment(self, commit):
        """
            Allows a doctor to accept the appointment
        :param doctor: Doctor to accept the appointment
        :param commit: indicates if the instance should be saved; used for testing
        :return: Boolean if the appointment was accepted or not
        """
        self.accept_state = Appointment.ACCEPTED
        if(commit):
            self.save()


    def rejectAppointment(self, commit):
        """
            Allows a doctor to reject the appointment
            :param doctor: Doctor to reject the appointment
            :param commit: indicates if the instance should be saved; used for testing
            :return: Boolean if the appointment was rejected or not
        """
        self.accept_state = Appointment.REJECTED
        if commit:
            self.save()

    def toggle_pending(self):
        """
            Toggles the state of the appointment back to pending
        :return: none
        """
        self.accept_state = Appointment.PENDING
        self.save()

class Hospital(models.Model):
    """
        Hospital class that represents a hopsital that is part of
        HealthNet. It keeps track of the different doctors, nurses, and
        patients.
    """

    ### FIELDS ###

    """The name of the hospital"""
    name = models.CharField(max_length=50)

    """Lists containing the doctors, nurses and patients part
        of the hospital"""
    doctors = []
    nurses = []
    patients = []
    prescriptionMasterList = []
    logEntries = []

    def addDoctor(self, doctor):
        """
            Adds a given doctor to the Hospital's list of doctors
        :param doctor: (Doctor) doctor to be added
        :return: none
        """
        self.doctors.append(doctor)

    def getDoctors(self):
        """
            Getter method for the list of doctors in the hospital
        :return: (list[Doctor])
        """
        return self.patient_doctors

    def addNurse(self, nurse):
        """
            Adds a given nurse to the Hospital's list of nurses
        :param nurse: (Nurse) nurse to be added
        :return: none
        """
        self.nurses.append(nurse)

    def getNurses(self):
        """
            Getter method for the list of nurses in the hospital
        :return: (list[Nurse])
        """
        return self.nurses

    def addPatient(self, patient):
        """
            Adds a given patient to the Hospital's list of patients
        :param patient: (Patient) patient to be added
        :return: none
        """
        self.patients.append(patient)

    def getPatients(self):
        """
            Getter method for the list of patients in the hospital
        :return: (list[Patients])
        """
        return self.patients

    def __str__(self):
        """
            String function that uses the hospital's name
        :return: (str) the hospital's name
        """

        return self.name



class HospitalAdmin(User):
    """
        Admins for specific Hospital
    """

    ### FIELDS ###

    """confirm a password"""
    confirm_password = models.CharField(max_length=20, default="")
    """hospital they are associated with"""
    hptal = models.ForeignKey('Hospital', null=False, verbose_name='Hospital')
    MALE = 'M'
    FEMALE = 'F'
    GENDER = (
        (MALE, "Male"),
        (FEMALE, "Female"))

    gender = models.CharField(max_length=1, null=True, choices=GENDER,
                              verbose_name='Gender')


    class Meta:
        """
            Changes the name of the model from User to Hospital Administrator in Django Admin Console
        """
        verbose_name = 'Hospital Administrator'
        verbose_name_plural = 'Hospital Administrators'

class Test(models.Model):
    """
        Tests to release to patients
    """

    #FIELDS#

    # Test that was ran
    name = models.CharField(max_length=50)

    # Results of the test
    results = models.TextField()

    # For the test results to be released, change status to true
    release = models.BooleanField(default=False)

    # Patient that the test is related to
    testPatient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    # Doctor that did the test
    testDoctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    # Date the test was done
    testDate = models.DateTimeField(default=django.utils.timezone.now)

    class Meta:
        """
            Changes the name of the model to Test in Django Admin Console
        """
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'

class Prescription(models.Model):
    """
    Class which represents a Prescription object that can be added/removed from
     a Patient.  Prescriptions are added/removed from a Patient only by the Doctor.
     Nurses can view the prescriptions of all Patients in their Hospital.  Patients
     can view their own Prescriptions.
    """

    ###FIELDS###

    # Name of the Prescription
    prescription_name = models.CharField(max_length=250)

    # Description of the Prescription
    description = models.CharField(max_length=500)

    # Patient whom the Prescription is assigned to
    patientAssigned = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='Prescribed_Patient',)

    # Doctor whom assigned the Prescription
    doctorAssigned = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='Prescribing_Doctor', )

    # Date the Prescription was assigned
    datePrescribed = models.DateField('Date Prescribed', default=date.today)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sender")
    receiver = models.ForeignKey(User, related_name="receiver", verbose_name="To")
    msg_content = models.TextField(verbose_name='', max_length=200)
    created_at = models.DateTimeField()
    status = models.BooleanField(default=False)

    def getUserType(self, user):
        if self.sender.id != user.id:
            return self.sender
        else:
            return self.receiver


def get_full_name(self):
    return self.first_name + " " + self.last_name

User.add_to_class("__str__", get_full_name)

class TransferRequest(models.Model):
    """
        Class that helps with the transfer of patients to and from a hospital.
        The parties that are able to transfer a patient is the Hospital Administrator
        as well as the doctor who is in charge of the patient. These transfers are
        request based, so that the admin/doctor will request to transfer a patient,
        and the recieving hospital will accept or reject the request. The patient's
        information will then be moved to that hospital.
    """

    ### FIELDS ###

    # the patient in question who shall be sent to a different hospital
    patient_to_transfer = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='Transferring_Patient', )

    # the hospital that the patient will transfer to
    receiving_hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='Receiving_hospital',)

    # the new doctor that the patient will be assigned to
    new_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='New_doctor',)

    # the admin who will recieve the request for the transfer
    receiving_admin = models.ForeignKey(HospitalAdmin, on_delete=models.CASCADE, related_name='Receiving_administrator', )

    # the doctor or hospital admin making this request
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Requester', )

    ### METHODS ###

    def description(self):
        """
            Returns a short description of the transfer request for display
        :return: (string) a description of the request
        """
        return 'Request to transfer ' + self.patient_to_transfer.first_name + ' ' + self.patient_to_transfer.last_name + \
                ' (' + self.patient_to_transfer.username + ')' + ' to ' + self.receiving_hospital.name + ' to be cared for by' + \
            ' Dr. ' + self.new_doctor.first_name + ' ' + self.new_doctor.last_name

    def accept_request(self):
        """
            Accepts the transfer request and "transfers" a patient to a different hospital
        :return: none
        """

        patient = self.patient_to_transfer

        patient.hospital = self.receiving_hospital
        patient.patient_doctor = self.new_doctor

        patient.save()

    def reject_request(self):
        """
            Rejects the transfer request and updates the reply associated with it
        :return: none
        """
        transfer_response = TransferRequestReply.objects.get(transfer_request__id=self.id, )
        transfer_response.acceptance_reply = TransferRequestReply.REJECTED
        transfer_response.save()

    def is_pending(self):
        """
            Determines state of request used in HTML template for display
        :return:
        """

        transfer_reply = TransferRequestReply.objects.filter(
            transfer_request__id = self.id
        )
        if(transfer_reply.first()):
            return (transfer_reply.first().acceptance_reply == TransferRequestReply.PENDING)
        else:
            return False


class TransferRequestReply(models.Model):
    """
        Class that is used to help with notifications about transfer requests after they are initially sent
        as well as when the response is given. The request has an optional "reason" field that the admin
        from the other hospital can use to give information as to why the transfer request was rejected
    """

    ### FIELDS ###

    # these are the possible replies that could be given in response to a transfer request
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    PENDING = 'Pending'

    ACCEPT_REPLY_CHOICES = (
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (PENDING, 'Pending')
    )

    # this is the Transfer Request associated with this reply
    transfer_request = models.ForeignKey(TransferRequest, on_delete=models.CASCADE, related_name='Transfer_request', blank=True)

    # this is the possible reply option associated with this transfer request
    acceptance_reply = models.SlugField(choices=ACCEPT_REPLY_CHOICES, default=PENDING)

    # this is the optional reason given as to why the request was denied
    reason = models.TextField(max_length=200, null=True)

    # this is the person who is associated with the receipt of this request
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Receiver',)

    def description(self):
        """
            Returns a short description used for display of the reply
        """
        if self.acceptance_reply != self.REJECTED or self.reason == None: # if not rejected, just use transfer_request description
            return self.transfer_request.description()
        else:
            return (self.transfer_request.description() +  " for this reason: " + self.reason)


class LogEntry(models.Model):
    """
    Model for an entry into the system log
    """

    #user who did an action that created an entry
    requester = models.ForeignKey(User, related_name="User_who_did_action")

    #the action that was done to make an entry
    action = models.CharField(max_length=50, blank=False)

    #the date and time the entry was logged
    date = models.DateTimeField()

    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = 'Entries'


class TimeFrame(models.Model):
    """
    model for time input to view system log
    """

    #lower boundry for time frame to view
    startTime = models.DateTimeField()

    #higher bound for time frame to view
    endTime = models.DateTimeField()


