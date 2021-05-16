from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from skill_matrix_app.forms import CreateUserForm, ChangePasswordForm
from skill_matrix_app.models import CustomUser, Admins, Workers
from skill_matrix_app.views import send_activation_email


def admin_home(request):
    all_users = CustomUser.objects.all().count()
    m_users = CustomUser.objects.filter(user_type="2").count()
    a_users = CustomUser.objects.filter(user_type="3").count()
    workers = Workers.objects.all().count()
    users_not_logged = CustomUser.objects.filter(last_login__isnull=True).count()
    users_logged = CustomUser.objects.filter(last_login__isnull=False).count()
    name_list = ('Administrator', 'Manager', 'Asystent')
    type_list = []
    for i in range(1, 4):
        types = CustomUser.objects.filter(user_type=i).count()
        type_list.append(types)



    print(all_users)
    print(m_users)
    print(a_users)
    print(workers)
    print(users_logged)
    context = {"all_users": all_users, "m_users": m_users, "a_users": a_users, "workers": workers, "type_list": type_list, "name_list": name_list, "users_not_logged": users_not_logged, "users_logged": users_logged}

    return render(request, 'admin_template/home_content.html', context)


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
            send_activation_email(request, user)
            messages.success(request, "Dodanie uzytkownika zakończone powodzeniem")
            return HttpResponseRedirect(reverse("manage_admin"))
        else:
            form = CreateUserForm(request.POST)
            messages.error(request, "Dodanie uzytkownika zakończone niepowodzeniem")
            return render(request, 'admin_template/add_admin_template.html', {"form": form})





def manage_admin(request):
    admins = CustomUser.objects.filter(user_type="1") & CustomUser.objects.exclude(
        is_superuser="1") & CustomUser.objects.exclude(id=request.user.id)
    form = CreateUserForm()
    return render(request, "admin_template/manage_admin_template.html", {"admins": admins, "form": form})


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
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            user_profile = Admins.objects.get(admin=request.user.id)
            if profile_pic_url != None:
                user_profile.profile_pic = profile_pic_url
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
    m_users = CustomUser.objects.order_by('managers__company_id__name') & CustomUser.objects.filter(user_type="2")
    a_users = CustomUser.objects.order_by('assistants__company_id__name') & CustomUser.objects.filter(user_type="3")


    return render(request, "admin_template/manage_users_template.html", {"m_users": m_users, "a_users": a_users})
