
"""
    Url patterns for all webpages in this project
"""

from django.conf.urls import url
from django.contrib.auth.views import login
from django.shortcuts import redirect

from . import views

urlpatterns = [
    url(r'^create_transfer_request/$', views.newTransferRequest, name='create_transfer_request'),
    url(r'^complete_transfer_request/(?P<patient>[0-9]+)/(?P<hospital>[0-9]+)/$', views.newTransferRequestComplete, name='complete_transfer_request'),
    url(r'^accept_request/(?P<req_id>[0-9]+)/$', views.acceptRequest, name='accept_request'),
    url(r'^reject_request/(?P<req_id>[0-9]+)/$', views.rejectRequest, name='reject_request'),
    url(r'^delete_request/(?P<req_id>[0-9]+)/$', views.deleteRequest, name='delete_request'),
    url(r'^reject_request_reason/(?P<req_id>[0-9]+)/$', views.rejectRequestForm, name='reject_request_reason'),
    url(r'^$', views.base, name='base'),
    url(r'^register_admin/$', views.admin_new, name='admin_new'),
    url(r'^register/$', views.patient_new, name='patient_new'),
    url(r'^register_patient/$', views.admin_patient_new, name='admin_patient_new'),
    url(r'^$', lambda _: redirect('admin:index'), name='admin_red'),
    url(r'^register_doctor/$', views.doctor_new, name='doctor_new'),
    url(r'^delete_doctor/(?P<doctor_id>[0-9]+)/$', views.delete_doctor, name='delete_doctor'),
    url(r'^delete_patient/(?P<patient_id>[0-9]+)/$', views.delete_patient, name='delete_patient'),
    url(r'^delete_admin/(?P<admin_id>[0-9]+)/$', views.delete_admin, name='delete_admin'),
    url(r'^register_nurse/$', views.nurse_new, name='nurse_new'),
    url(r'^message_new/', views.message_new, name='message_new'),
    url(r'^view_conversation/(?P<name>[-\w]+)/$', views.view_conversation, name='view_conversation'),
    url(r'^reply/(?P<otheruser_name>[-\w]+)/$', views.reply, name='reply'),
    url(r'^delete_nurse/(?P<nurse_id>[0-9]+)/$', views.delete_nurse, name='delete_nurse'),
    url(r'^employees/$', views.employees, name='employees'),
    url(r'^patients/$', views.patients, name='patients'),
    url(r'^patient_list/$', views.patient_list, name='patient_list'),
    url(r'^create_test/$', views.createTest, name='create_test'),
    url(r'^review_test/$', views.reviewTest, name='review_test'),
    url(r'^message/$', views.message, name='message'),
    url(r'^test_results/$', views.test_results, name='test_results'),
    url(r'^review_test/(?P<test_id>[0-9]+)/$', views.releaseTest, name='release_test'),
    url(r'^review_test_images/(?P<test_id>[0-9]+)/$', views.testImages, name='test_images'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', views.logout_user, name='logout_user'),
    url(r'^calendar/$', views.baseCalendar, name='base_calendar'),
    url(r'^calendar/(?P<themonth>[0-9]+)/(?P<theyear>[0-9]{4})$', views.calendar, name='calendar'),
    url(r'^appointment/(?P<day>[0-9]+)/(?P<month>[0-9]+)/(?P<year>[0-9]{4})$', views.day_view, name='day_view'),
    url(r'^calendar/create_appointment/$', views.createAppointment,
        name='create_appointment'),
    url(r'^calendar/update_appointment/(?P<appt_id>[0-9]+)/$', views.updateAppointment,
        name='edit_appointment'),
    url(r'^delete_appointment/(?P<appt_id>[0-9]+)/$', views.deleteAppointment, name='delete_appointment'),
    url(r'^accept_appointment/(?P<appt_id>[0-9]+)/$', views.acceptAppointment, name='accept_appointment'),
    url(r'^reject_appointment/(?P<appt_id>[0-9]+)/$', views.rejectAppointment, name='reject_appointment'),
    url(r'^patient_info/$', views.patient_info, name='patient_info'),
    url(r'^patient_edit/$', views.patient_edit, name='patient_edit'),
    url(r'^prescriptions/(?P<patient_id>[0-9]+)/$', views.viewPatientPrescriptions, name='prescriptions'),
    url(r'^prescriptions/new_prescription/(?P<patient_id>[0-9]+)/$', views.newPrescription, name='new_prescription'),
    url(r'^prescriptions/edit_prescription/(?P<prescrip_id>[0-9]+)/$', views.updatePrescription, name='edit_prescription'),
    url(r'^prescriptions/review_prescription/(?P<prescrip_id>[0-9]+)/$', views.reviewPrescription, name='review_prescription'),
    url(r'^prescriptions/delete_prescription/(?P<prescrip_id>[0-9]+)/$', views.deletePrescription, name='delete_prescription'),
    url(r'^patient_info_emp/(?P<patient_id>[0-9]+)/$', views.patient_info_emp, name='patient_info_emp'),
    url(r'^med_info_edit/(?P<patient_id>[0-9]+)/$', views.med_info_edit, name='med_info_edit'),
    url(r'^change_hosp_status/(?P<patient_id>[0-9]+)/$', views.change_hosp_status, name='change_hosp_status'),
    url(r'^patient_info/export/$', views.export, name='export'),
    url(r'^log/$', views.systemStats, name='log'),
    url(r'^time_entry/$', views.timeFrameInput, name='time_entry'),
]


