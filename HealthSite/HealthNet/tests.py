"""
    This file contains several test cases that can easily be verified through
    code instead of manually testing the website.

    Current tests present are for testing the functions manipulating the
    data of the models, namely the Appointment model and the Note model.
    Other models are not present due to the fact that Django forms and generic
    class views are used when manipulating their data, and these functions are
    safe enough that an interactive test can be used instead.

    @author: Theodora Bendlin
"""


from django.test import TestCase
from .models import Patient, Appointment, Doctor
from .forms import CreateAppointmentForm
from .calendar import Month
from django.utils import timezone
import datetime

class AppointmentTests(TestCase):

    def test_init(self):
        """
            Should create an appointment at the given time
        """
        time = timezone.now() + datetime.timedelta(days=5)
        appt = Appointment(appointment_time=time, reason="Test", patient=Patient(), doctor=Doctor())

        self.assertTrue(isinstance(appt, Appointment))

    def test_modify_appointment(self):
        """
            Should modify the given fields of the appointment. The accept state should return
            to pending
        """
        time = timezone.now() + datetime.timedelta(days=5)
        doctor = Doctor()
        patient = Patient()

        appt = Appointment(appointment_time=time, reason="Test", patient=patient, doctor=doctor)
        appt.modify_appointment(date_time=time, doctor=Doctor(), reason="Testing")
        self.assertEqual(appt.reason, "Testing")
        self.assertEqual(appt.accept_state, Appointment.PENDING)

    def test_accept_appointment(self):
        """
            Test to make sure that the accept state of the Appointment is changed
            to accepted once the doctor accepts the appointment
        """
        time = timezone.now() + datetime.timedelta(days=5)
        doctor = Doctor()
        patient = Patient()

        appt = Appointment(appointment_time=time, reason="Test", patient=patient, doctor=doctor)
        appt.acceptAppointment(commit=False)
        self.assertEqual(appt.accept_state, Appointment.ACCEPTED)

    def test_reject_appointment(self):
        """
            Test to make sure that the accept state of the Appointment is changed
            to rejected once the doctor rejects the appointment
        """
        time = timezone.now() + datetime.timedelta(days=5)
        doctor = Doctor()
        patient = Patient()

        appt = Appointment(appointment_time=time, reason="Test", patient=patient, doctor=doctor)
        appt.rejectAppointment(commit=False)
        self.assertEqual(appt.accept_state, Appointment.REJECTED)


    def test_accept_then_modify(self):
        """
            Test to ensure that an appointment that has been accepted will return to being
            in the "pending" state once modified
        """
        time = timezone.now() + datetime.timedelta(days=5)
        doctor = Doctor()
        patient = Patient()

        appt = Appointment(appointment_time=time, reason="Test", patient=patient, doctor=doctor)
        appt.acceptAppointment(commit=False)
        self.assertEqual(appt.accept_state, Appointment.ACCEPTED)

        appt.modify_appointment(date_time=time, doctor=doctor, reason="Testing")
        self.assertEqual(appt.reason, "Testing")
        self.assertEqual(appt.accept_state, Appointment.PENDING)

class AppointmentFormTests(TestCase):
    """
        Class dedicated to testing the form validation for appointment times
    """

    def test_appointment_in_the_past(self):
        """
             Test to ensure that an appointment cannot have a time in the past
        """

        # fields needed for an appointment form
        time = timezone.now() + datetime.timedelta(days=-5)

        # initialize the appointment form
        apptForm = CreateAppointmentForm(initial={'doctor': Doctor.objects.all().first(),
                                                  'patient': Patient.objects.all().first(),
                                                  'reason': "Test",
                                                  'appointment_time': time })

        # make sure that the validation returns false
        self.assertEqual(apptForm.is_valid(), False)

class MonthClassTests(TestCase):
    """
        Class dedicated to testing simple functions for checking the correct
        initialization of a month object
    """

    def test_month_with_defaults(self):
        """
            Test to make sure that sending in a -1 will make the month default
             to the current year and month
        """
        month = datetime.date.today().month  # default for month is this month
        year = datetime.date.today().year  # default for year is this year

        model = Month(-1, -1)

        self.assertEqual(model.month, month)
        self.assertEqual(model.year, year)

    def test_month_without_defaults(self):
        """
            Test to make sure that sending in an actual month and year
            will have these values as the month and year
        """
        month = 7
        year = 1997

        model = Month(month, year)

        self.assertEqual(model.month, month)
        self.assertEqual(model.year, year)

    def test_month_with_invalid_month(self):
        """
            Test to make sure that sending in an invalid month and
            valid year will result in the correct month
        """
        month = -7
        year = 1997

        model = Month(month, year)

        self.assertEqual(model.month, datetime.date.today().month)
        self.assertEqual(model.year, year)

    def test_month_with_default_month_and_valid_year(self):
        """
            Test to make sure that sending in the default month value and
            valid year will result in the correct month
        """
        year = 1997

        model = Month(-1, year)

        self.assertEqual(model.month, datetime.date.today().month)
        self.assertEqual(model.year, year)

    def test_month_with_invalid_year(self):
        """
            Test to make sure that sending in an invalid year and
            valid month will result in the correct month object
        """
        month = 7
        year = 0

        model = Month(month, year)

        self.assertEqual(model.month, month)
        self.assertEqual(model.year, datetime.date.today().year)

    def test_month_with_default_year_and_valid_month(self):
        """
            Test to make sure that sending in the default month value and
            valid year will result in the correct month
        """
        month = 8

        model = Month(month, -1)

        self.assertEqual(model.month, month)
        self.assertEqual(model.year, datetime.date.today().year)

    def test_calulate_starting_day(self):
        """
            Tests the successful calculation of the day that starts the week
             for a given month
        """

        month1 = Month(-1, -1)
        month2 = Month(1, 2016)
        month3 = Month(9, 2018)

        # starting days of the week are 0-6, sunday to saturday
        self.assertEqual(month1.calculate_starting_day(), 1)    # Monday
        self.assertEqual(month2.calculate_starting_day(), 5)    # Friday
        self.assertEqual(month3.calculate_starting_day(), 6)    # Saturday

    def test_fill_days(self):
        """
            Tests the successful calculation of the day that starts the week
             for a given month
        """

        month1 = Month(-1, -1)
        month2 = Month(1, 2016)
        month3 = Month(9, 2018)

        # starting days of the week are 0-6, sunday to saturday
        # check that the numberation for the month starts on that day
        self.assertEqual(month1.get_days()[1], 1)  # Monday
        self.assertEqual(month2.get_days()[5], 1)  # Friday
        self.assertEqual(month3.get_days()[6], 1)  # Saturday