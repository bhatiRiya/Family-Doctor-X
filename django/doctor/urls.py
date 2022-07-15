from django.urls import path
from .views import HomeTemplateView, AppointmentTemplateView, ManageAppointmentTemplateView
from .views import *
urlpatterns = [
    path("", HomeTemplateView.as_view(), name="home"),
    path("make-an-appointment/", AppointmentTemplateView.as_view(), name="appointment"),
    path("manage-appointments/", ManageAppointmentTemplateView.as_view(), name="manage"),
    path('logoutWA', logout_client, name='logoutWA'),
    path('rebootWA', reboot_client, name='rebootWA'),
    path('getQrCode', get_qr_code, name='getQrCode'),
    path('getQrStatus', get_qr_status, name='getQrStatus'),
]