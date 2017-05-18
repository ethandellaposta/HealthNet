"""
    File containing the classes needed for a calendar implementation
    @author Theodora Bendlin
"""
import datetime
from datetime import date
from django.core.urlresolvers import reverse
from .models import Appointment

class Month(object):

    ### CONSTANTS ###

    # The months shifted so that March = 1, February = 12
    # this array is used in the calculation for finding
    # the first day of a month
    shifted_months = [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # the number of days in a month
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    ### FIELDS ###
    month = datetime.date.today().month # default for month is this month
    year = datetime.date.today().year   # default for year is this year
    days = []                               # a list representing all of the days
                                            # index 0 represents a sunday

    def __init__(self, month, year):
        """
            Initialization for a month. If a month or year should use the
            defaults, then a value of -1 is passed in. Otherwise, the passed
            in value is used. Months are enumerated from 1 - 12.

            Assumptions:
                The given year and month values are valid

        :param month: (int) the current month
        :param year:  (int) the current year
        """

        if(month != -1 ):       # we don't want to use the default
            self.month = month

        if(year != -1):         # we don't want to use the default
            self.year = year

        # fill in the days so that they are aligned by day of the
        # week
        self.days = self.fill_days()


    def calculate_starting_day(self):
        """
            Determines the starting day of the given month using the
            following formula:

            w = ( d + floor(2.6m - 0.2) + Y + floor(y/4) + floor(c/4)
                    -2c ) % 7
            where:
                Y is the year minus 1 for January/February, and the year
                for any other month (0 - 100)
                y is the last 2 digits of Y
                c is the first 2 digits of Y
                d is the day of the month

        :return: (int) the starting day for this month ( 0 is sunday, 6 is
                                                            saturday )
        """

        m = self.shifted_months[self.month - 1]  # the month in question shifted for the formula
        c = int(str(self.year)[:2])              # the century in question

        Y = self.year % 100                      # getting the year. Numbered 1 - 100
        if(Y == 0):
            Y = 100

        # shifting the year if it is January or February
        if( (m == 11) or (m == 12)):
            Y = Y - 1

        term1 = int( (2.6 * m) - 0.2)
        term2 = int(Y/4)
        term3 = int(c/4)

        return (1 + term1 + Y + term2 + term3 - (2 * c)) % 7


    def is_leap_year(self):
        """
            Determines if a month's year is a leap year
        :return True if the month is a leap year, False otherwise
        """

        if((self.year % 4) == 0):
            if((self.year % 100) == 0):
                if((self.year % 400) == 0):
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    def fill_days(self):
        """
            Fills in the days array for the given month such that
            the numeration for the days begins on the starting day
            for that month

            Days are numbered 0 - 6

        """

        starting_day = self.calculate_starting_day()
        currDay = 0
        days = []

        # Append 0s while we are not on the starting day
        while(currDay < starting_day):
            days.append(0)
            currDay = currDay + 1

        num_of_days = self.days_in_month[self.month - 1]
        if(self.is_leap_year() and (self.month == 2)):
            num_of_days = num_of_days + 1

        # now we are on the correct starting day
        # so it is time to fill in all of
        # the days in the month
        for day in range(num_of_days):
            days.append(day + 1)

        return days

    def get_days(self):
        """ Getter function for the days display """
        return self.days

class ApptCalendar(object):

    ### CONSTANTS ###
    months = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May",
        6: "June", 7: "July", 8: "August", 9: "September", 10: "October",
        11: "November", 12: "December"
    }

    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday",
             "Thursday", "Friday", "Saturday"]

    def __init__(self, month, year, appts):
        """
            Init function for a calendar that will group
            the appointments by day
        :param appointments:
        """
        self.month = month
        self.year = year
        self.appointments = self.group_days(appts)

    def get_absolute_url(self, day):
        """
            Returns the url for the day view of the given day
        :param day: the day in question
        :return: reverse for day view
        """
        return reverse('day_view', kwargs={'day': day,
                                           'month': self.month,
                                           'year': self.year})

    def day_cell(self, cssclass, day):
        """
            Formatting method for day_cells
        :param cssclass: the cssclas to use
        :param body: the body of the cell
        :return: the formatting tag for day_cells
        """
        if day != 0:
            return '<td class="%s"><a href="%s">%s</a></td>' % (cssclass, self.get_absolute_url(day), day)
        return'<td class="%s">&nbsp;</td>' % cssclass

    def format_day(self, day):
        """
            Formats a day. If the day is 0, then it is represented by
            an empty space. Otherwise, it's number is put into <td> tags
        :return: (str) the HTML representation of a day
        """
        if day != 0:
            cssclass = ''
            if date.today() == date(self.year, self.month, day):
                cssclass += 'today'
            if day in self.appointments:
                for appt in self.appointments[day]:
                    if appt.accept_state == Appointment.REJECTED:
                        cssclass+= ' rejected'
                        break
                    elif appt.accept_state == Appointment.PENDING:
                        cssclass += ' pending'
                    else:
                        cssclass += ' filled'
                return self.day_cell(cssclass, day)
            else:
                cssclass += ' unfilled'
                return self.day_cell(cssclass, day)
        return self.day_cell('noday', 0)

    def format_week(self, week):
        """
            Formats a week as a complete table row
        :param week: the slice of the week that is being formatted
        :return: (str) the week
        """
        s = ''.join(self.format_day(d) for d in week)
        return '<tr class=\"days\">%s</tr>' % s

    def format_week_header(self):
        """
            Formats the week header
        :return: (str) the string representation
        """
        s = '<tr class=\"weekdays\">'
        for i in range(7):
            s += '<th>' + self.weekdays[i] + '</th>'
        return s + '</tr>'

    def format_month(self, themonth, theyear):
        """
            Return a month as an HTML table
        :param month: the month to represent
        :param year:  the year
        :return: (str) the HTML markup to represent the month
        """
        month = Month(themonth, theyear)

        html = ['<table class=\"month\">']
        html.append('\n')
        html.append(self.format_week_header())

        iterator = 0
        week = []
        for day in month.days:
            if(iterator < 7):                                   # the full week isn't full
                week.append(day)
                iterator += 1

                if ((iterator == 7)):  # if one week has been added to the array,
                    # then it is time to add it to the html
                    html.append(self.format_week(week))
                    html.append('\n')
                    week = []
                    iterator = 0

        if(iterator != 0):                          # then there are still days to add
            while(iterator != 7):
                week.append(0)
                iterator += 1
            html.append(self.format_week(week))
            html.append('\n')


        html.append('</table>')
        html.append('\n')
        return ''.join(html)

    def group_days(self, appointments):
        """
            Function that returns a dictionary of appointments grouped
            by day
            :param appointments: List of appointments held in the calendar
            :return: a dictionary of days with appointments as the values
        """
        appt_by_day = {}
        appointments = list(appointments)

        for appt in appointments:
            day = appt.appointment_time.day
            if not appt_by_day.__contains__(day):
                appt_by_day[day] = [appt]
            else :
                appt_by_day[day].append(appt)

        return appt_by_day

class DoctorCalendar(ApptCalendar):

    def __init__(self, month, year, appointments):
        ApptCalendar.__init__(self, month, year, appointments)

    def format_day(self, day):
        """
            Formats a day. If the day is 0, then it is represented by
            an empty space. Otherwise, it's number is put into <td> tags
        :return: (str) the HTML representation of a day
        """
        if day != 0:
            cssclass = ''
            if date.today() == date(self.year, self.month, day):
                cssclass += 'today'
            if day in self.appointments:
                for appt in self.appointments[day]:
                    if appt.accept_state == Appointment.PENDING:
                        cssclass+= ' pending'
                        break
                cssclass += ' filled'
                return self.day_cell(cssclass, day)
            else:
                cssclass += ' unfilled'
                return self.day_cell(cssclass, day)
        return self.day_cell('noday', 0)

    def group_days(self, appointments):
        """
            Function that returns a dictionary of appointments grouped
            by day
            :param appointments: List of appointments held in the calendar
            :return: a dictionary of days with appointments as the values
        """
        appt_by_day = {}
        appointments = list(appointments)

        for appt in appointments:
            if appt.accept_state != Appointment.REJECTED:
                day = appt.appointment_time.day
                if not appt_by_day.__contains__(day):
                    appt_by_day[day] = [appt]
                else :
                    appt_by_day[day].append(appt)

        return appt_by_day