"""
    File containing all models that are registered for the admin

    @authors: Theodora Bendlin, Ethan Della Posta, Laura Corrigan, Benjamin Kirby, Eliott Frilet
"""

from django.contrib import admin
from . import models
from . import forms


class AppointmentAdmin(admin.ModelAdmin):
    exclude = ('accept_state',)

class HospitalAdminAdmin(admin.ModelAdmin):
    exclude = ('is_staff', 'is_active', 'is_superuser','date_joined', 'user_permissions', 'groups', 'last_login')
    form = forms.HospitalAdminForm

admin.site.register(models.Patient)
admin.site.register(models.Appointment, AppointmentAdmin)
admin.site.register(models.Doctor)
admin.site.register(models.Nurse)
admin.site.register(models.Hospital)
admin.site.register(models.HospitalAdmin, HospitalAdminAdmin)
admin.site.register(models.Prescription)
admin.site.register(models.Message)
admin.site.register(models.TransferRequest)
admin.site.register(models.TransferRequestReply)
admin.site.register(models.Test)
admin.site.register(models.LogEntry)
