from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
import requests
from django.views.generic.base import TemplateView
from django.core.mail import EmailMessage, message
from django.conf import settings
from django.contrib import messages
from .models import Appointment
from django.views.generic import ListView
import datetime
from django.template import Context
from django.template.loader import render_to_string, get_template
from .models import *
from .whatsapp_client_api import WABot


class HomeTemplateView(TemplateView):
    template_name = "index.html"
    
    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        email = EmailMessage(
            subject= f"{name} from doctor family.",
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_HOST_USER],
            reply_to=[email]
        )
        email.send()
        return HttpResponse("Email sent successfully!")


class AppointmentTemplateView(TemplateView):
    template_name = "appointment.html"

    def post(self, request):
        fname = request.POST.get("fname")
        lname = request.POST.get("fname")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        message = request.POST.get("request")

        appointment = Appointment.objects.create(
            first_name=fname,
            last_name=lname,
            email=email,
            phone=mobile,
            request=message,
        )

        appointment.save()

        messages.add_message(request, messages.SUCCESS, f"Thanks {fname} for making an appointment, we will email you ASAP!")
        return HttpResponseRedirect(request.path)




def check_authentication(request):
    request.session['WA_BOT_AUTH_STATUS'] = None
    try:
        obj_whats_app_bot = WABot()
        request.session['WA_BOT_AUTH_STATUS'] = obj_whats_app_bot.accountStatusActive
    except Exception as e:
        return str(e)


def logout_client(request):
    rtn_data = {}
    try:
        wa_bot = WABot()
        response = wa_bot.logout()
        if response == 'Logout request sent to WhatsApp':
            request.session['WA_BOT_AUTH_STATUS'] = False
            rtn_data['status'] = "SUCCESS"
        else:
            rtn_data['status'] = "FAILED"
    except Exception as e:
        rtn_data['status'] = str(e)
    return JsonResponse(rtn_data)



def reboot_client(request):
    rtn_data = {}
    try:
        wa_bot = WABot()
        response = wa_bot.reboot()
        if response and response != "client is not authenticated":
            request.session['WA_BOT_AUTH_STATUS'] = wa_bot.accountStatusActive
            rtn_data['status'] = "SUCCESS"
        else:
            rtn_data['status'] = "FAILED"
    except Exception as e:
        rtn_data['status'] = str(e)
    return JsonResponse(rtn_data)



def get_qr_code(request):
    rtn_data = {}
    wa_bot = WABot()
    file_path = wa_bot.get_qr_code()
    if file_path and file_path != "Client already registered! please logout first to display QR code.":
        rtn_data['status'] = "SUCCESS"
        rtn_data['file_path'] = str(file_path)
    else:
        rtn_data['status'] = "FAILED"
    return JsonResponse(rtn_data)


def get_qr_status(request):
    check_authentication(request)
    rtn_data = {}
    if request.session['WA_BOT_AUTH_STATUS']:
        rtn_data['status'] = "SUCCESS"
    else:
        rtn_data['status'] = "FAILED"
    return JsonResponse(rtn_data)


class ManageAppointmentTemplateView(ListView):
    template_name = "manage-appointments.html"
    model = Appointment
    context_object_name = "appointments"
    login_required = True
    paginate_by = 3



    def post(self, request):
        date = request.POST.get("date")
        appointment_id = request.POST.get("appointment-id")
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.accepted = True
        appointment.accepted_date = datetime.datetime.now()
        appointment.save()

        try:
            appoiment = Appointment.objects.get(id=appointment_id)
            wa_bot = WABot()
            welcome_msg = "Hi {}, I'm a whatsApp bot controlled by Wizard Engineering, My duties are alert users/ " \
                        "employees who are linked with our products. " \
                        "This a test message to verify registered users, so do not reply to this message. Hope we can " \
                        "communicate better. ".format(appoiment.first_name)

            response = wa_bot.send_message_by_chat_id(chatId=appoiment.id, text=welcome_msg)
            if response and response != 'client is not authenticated':
                appoiment.is_verify = True
                appoiment.save()
                messages.add_message(request, messages.SUCCESS, "Message successfully send")
                generate_activity_log(request,  user=appoiment.first_name, action='verified')
            else:
                messages.add_message(request, messages.WARNING, "Something went wrong! please try again sometime")
        except Exception as e:
            messages.add_message(request, messages.WARNING, e)
        
        messages.add_message(request, messages.SUCCESS, f"You accepted the appointment of {appointment.first_name}")
        return HttpResponseRedirect(request.path)

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        appointment = Appointment.objects.all()
        context.update({   
            "title":"Manage Appointments"
        })
        return context

def generate_activity_log(request, category="", user="", action=""):
    now = datetime.datetime.now()
    formatted = now.strftime("%a  %d-%b-%Y  %I:%M %p")
    if action and user and category:
        ActivityLogs(
            activity="{} {} {} by {} on {}".format(category, user, action, request.session['admin']['username'],
                                                   formatted)).save()