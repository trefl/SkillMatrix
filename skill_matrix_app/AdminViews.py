from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from skill_matrix_app.forms import AddManagerForm, AddAdminForm, CreateUserForm, ChangePasswordForm
from skill_matrix_app.models import CustomUser, Companies, Admins, Managers, Assistants
from skill_matrix_app.views import send_activation_email


def admin_home(request):
    return render(request, 'admin_template/home_content.html')


def add_admin(request):
    form = CreateUserForm()

    return render(request, 'admin_template/add_admin_template.html', {'form': form})




def add_admin_save(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    else:
        form = CreateUserForm(request.POST)
        if form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')

            user = CustomUser.objects.create_user(username=email, email=email, last_name=last_name, first_name=first_name, user_type=1)
            user.set_password(CustomUser.objects.make_random_password())
            user.save()
            #-------------
            send_activation_email(request, user)

            #--------------
            messages.success(request, "Dodanie uzytkownika zakończone powodzeniem")
            return HttpResponseRedirect(reverse("manage_admin"))
        else:
            form = CreateUserForm(request.POST)
            messages.error(request, "Dodanie uzytkownika zakończone niepowodzeniem")
            return render(request, 'admin_template/add_admin_template.html', {"form": form})
            # return HttpResponseRedirect(request("manage_admin"))






# def send_activation_email(request, user, use_https=False, from_email=None):
#     current_site = get_current_site(request)
#     print(current_site)
#     token_generator = PasswordResetTokenGenerator()
#     print(token_generator)
#     token = token_generator.make_token(user)
#     print(token)
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#     print(uid)
#     site_name = current_site.name
#     print(site_name)
#     domain = current_site.domain
#     print(domain)
#     admin = request.user
#     print(admin)
#     c = {
#         'email': user.email,
#         'domain': domain,
#         'site_name': site_name,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'user': user,
#         'token': token_generator.make_token(user),
#         'protocol': 'https' if use_https else 'http',
#         'admin': admin,
#     }
#     subject_template_name = 'registration/password_reset_subject.txt',
#     email_template_name = 'registration/invite_user_email.html',
#     subject = loader.render_to_string(subject_template_name, c)
#     # Email subject *must not* contain newlines
#     subject = ''.join(subject.splitlines())
#     email = loader.render_to_string(email_template_name, c)
#     send_mail(subject, email, from_email, [user.email])




def add_manager(request):
    return render(request, 'admin_template/add_manager_template.html')


def add_manager_save(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    else:
        form = AddManagerForm(request.POST)
        if form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            company = request.POST.get('company')

            company_model = Companies(name=company)
            company_model.save()

            user = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                  last_name=last_name, first_name=first_name, user_type=2)
            user.managers.company_id_id = company_model.id
            user.save()
            # return print(company_model.id)

            messages.success(request, "Successfully Added Manager ")
            return HttpResponseRedirect(reverse("add_manager"))
        else:
            form = AddManagerForm(request.POST)
            return render(request, 'admin_template/add_manager_template.html', {"form": form})


def add_assistant(request):
    return render(request, 'admin_template/add_assistant_template.html')


def manage_admin(request):
    admins = CustomUser.objects.filter(user_type="1") & CustomUser.objects.exclude(
        is_superuser="1") & CustomUser.objects.exclude(id=request.user.id)
    form = CreateUserForm()
    return render(request, "admin_template/manage_admin_template.html", {"admins": admins, "form": form})
    print(admins)


def delete_admin(request, admin_id):
    admin = CustomUser.objects.get(id=admin_id)

    if (request.user.is_superuser is True) & (int(admin_id) != request.user.id) & (admin.user_type == "1"):
        admin.delete()
        messages.success(request, "Profil został zaktualizowany")
        return HttpResponseRedirect(reverse("manage_admin"))
    else:
        messages.error(request, "Aktualizacja profilu nieudana")
        return HttpResponseRedirect(reverse("manage_admin"))


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, "admin_template/admin_profile_template.html", {"user": user})


def admin_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse(admin_profile))
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        if request.FILES.get('profile_pic', False):
            profile_pic = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)
        else:
            profile_pic_url = None

        try:
            user = CustomUser.objects.get(id=request.user.id)
            print(user)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            user_profile = Admins.objects.get(admin=request.user.id)
            if profile_pic_url != None:
                user_profile.profile_pic = profile_pic_url
            print(user_profile)
            user_profile.save()

            messages.success(request, "Profil został zaktualizowany")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request, "Aktualizacja profilu nieudana")
            return HttpResponseRedirect(reverse("admin_profile"))



def admin_change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Zmian hasła zakończona sukcesem')
            return redirect('admin_profile')
    else:
        form = ChangePasswordForm(request.user)

    return render(request, "admin_template/change_password_template.html", {"form": form})



def manage_users(request):
    # users = CustomUser.objects.exclude(user_type="1")

    m_users = CustomUser.objects.order_by('managers__company_id__name') & CustomUser.objects.filter(user_type="2")
    a_users = CustomUser.objects.order_by('assistants__company_id__name') & CustomUser.objects.filter(user_type="3")


    return render(request, "admin_template/manage_users_template.html", {"m_users": m_users, "a_users": a_users})
