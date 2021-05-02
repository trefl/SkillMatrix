import requests as requests
import json
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template import loader


# Create your views here.
from django.urls import reverse

from skill_matrix_app.EmailBackEnd import EmailBackEnd
from skill_matrix_app.forms import SignupManagerForm, CreateUserForm
from skill_matrix_app.models import CustomUser, Companies


def showDemoPage(request):
    return render(request, "demo.html")


def ShowLoginPage(request):
    return render(request, "login_page.html")


def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2> Method Not Allowed</h2>")
    else:
        captcha_token = request.POST.get("g-recaptcha-response")
        cap_url = "https://www.google.com/recaptcha/api/siteverify"
        cap_secret = "6LfkwbYaAAAAAMJVc2-6rZxTLypHMohbAOXg1OnD"
        cap_data = {"secret": cap_secret, "response": captcha_token}
        cap_server_response = requests.post(url=cap_url, data=cap_data)
        cap_json = json.loads(cap_server_response.text)

        if cap_json['success'] == False:
            messages.error(request, "Nieprawidłowy Captcha, spróbuj ponownie")
            return HttpResponseRedirect("/")

        user = EmailBackEnd.authenticate(request, username=request.POST.get("email"),
                                         password=request.POST.get("password"))
        if user != None:
            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect('/admin_home')
            elif user.user_type == "2":

                return HttpResponseRedirect(reverse("manager_home"))
            else:
                return HttpResponseRedirect(reverse("assistant_home"))
        else:
            messages.error(request, "Nieudane Logowanie")
            return HttpResponseRedirect("/")


def GetUserDetails(request):
    if request.user != None:
        return HttpResponse("User:" + request.user.email + "usertype: " + str(request.user.user_type))
    else:
        return HttpResponse("Please login First")


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")


def signup_admin(request):
    form = CreateUserForm()

    return render(request, "signup_admin_page.html", {'form': form})


def signup_manager(request):
    form = SignupManagerForm()
    return render(request, "signup_manager_page.html", {'form': form})


def do_admin_signup(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    else:

        form = CreateUserForm(request.POST)
        if form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            user = CustomUser.objects.create_user(username=email, password=password, first_name=first_name, last_name=last_name, email=email, user_type=1)
            user.save()

            messages.success(request, "Rejestracja zakończona sukcesem. Możesz się zalogować")
            return HttpResponseRedirect(reverse("signup_admin"))

        else:
            form = CreateUserForm(request.POST)
            return render(request, 'signup_admin_page.html', {"form": form})




def do_manager_signup(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    else:
        form = SignupManagerForm(request.POST)
        if form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            company = request.POST.get('company')

            company_model = Companies(name=company)
            company_model.save()

            user = CustomUser.objects.create_user(username=email, password=password, first_name=first_name, last_name=last_name, email=email, user_type=2)
            user.managers.company_id_id = company_model.id
            user.save()

            messages.success(request, "Rejestracja zakończona sukcesem. Możesz się zalogować")
            return HttpResponseRedirect(reverse("show_login"))
        else:
            form = SignupManagerForm(request.POST)
            return render(request, 'signup_manager_page.html', {"form": form})




def send_activation_email(request, user, use_https=False, from_email=None):
    current_site = get_current_site(request)
    token_generator = PasswordResetTokenGenerator()
    site_name = current_site.name
    domain = current_site.domain
    admin = request.user
    c = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'user': user,
        'token': token_generator.make_token(user),
        'protocol': 'https' if use_https else 'http',
        'admin': admin,
    }
    subject_template_name = 'registration/password_reset_subject.txt',
    email_template_name = 'registration/invite_user_email.html',
    subject = loader.render_to_string(subject_template_name, c)
    subject = ''.join(subject.splitlines())
    email = loader.render_to_string(email_template_name, c)
    send_mail(subject, email, from_email, [user.email])