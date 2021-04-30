from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from skill_matrix_app.forms import AddManagerForm, AddAssistantForm, ChangePasswordForm, CreateUserForm
from skill_matrix_app.models import CustomUser, Companies, Managers, Assistants
from skill_matrix_app.views import send_activation_email


def manager_home(request):
    # print(request.user.id)
    # print(request.user.managers.company_id_id)
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    # print(company.name)
    # print(company.id)

    return render(request, 'manager_template/home_content.html', {"company": company})



def add_assistant(request):
    form = CreateUserForm()

    return render(request, 'manager_template/add_assistant_template.html', {"form": form})

def manage_assistant(request):
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    assistants = Assistants.objects.filter(company_id=company.id)
    form = CreateUserForm()
    # print(request.user.id)

    return render(request, "manager_template/manage_assistant_template.html", {"assistants": assistants, "form": form})

def delete_assistant(request, assistant_id):
    print(assistant_id)
    user = CustomUser.objects.get(id=assistant_id)
    print(user.assistants.company_id.id)
    print(request.user.managers.company_id_id)

    if (user.assistants.company_id.id == request.user.managers.company_id_id):
        user.delete()
        messages.success(request, "Profil został usunięty")
        return HttpResponseRedirect(reverse("manage_assistant"))
    else:
        messages.error(request, "Usunięcie profilu nieudana")
        return HttpResponseRedirect(reverse("manage_assistant"))


def add_assistant_save(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    else:
        form = CreateUserForm(request.POST)
        if form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')

            company = Companies.objects.get(id=request.user.managers.company_id_id)
            user = CustomUser.objects.create_user(username=email, email=email, last_name=last_name, first_name=first_name, user_type=3)
            user.set_password(CustomUser.objects.make_random_password())
            user.assistants.company_id_id = company.id
            user.save()

            send_activation_email(request, user)

            messages.success(request, "Dodanie uzytkownika zakończone powodzeniem")
            return HttpResponseRedirect(reverse("manage_assistant"))
        else:
            form = CreateUserForm(request.POST)
            messages.error(request, "Dodanie uzytkownika zakończone niepowodzeniem")
            return render(request, 'manager_template/add_assistant_template.html', {"form": form})
            # return HttpResponseRedirect(request("manage_assistant"))




def manager_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    return render(request, "manager_template/manager_profile_template.html", {"user": user, "company": company})

def manager_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse(manager_profile))
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
            user_profile = Managers.objects.get(admin=request.user.id)
            if profile_pic_url != None:
                user_profile.profile_pic = profile_pic_url
            user_profile.save()

            messages.success(request, "Profil został zaktualizowany")
            return HttpResponseRedirect(reverse("manager_profile"))
        except:
            messages.error(request, "Aktualizacja profilu nieudana")
            return HttpResponseRedirect(reverse("manager_profile"))

def manager_company_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse(manager_profile))
    else:
        company_name = request.POST.get("company_name")

        if request.FILES.get('logo_pic', False):
            logo_pic = request.FILES['logo_pic']
            fs = FileSystemStorage()
            filename = fs.save(logo_pic.name, logo_pic)
            logo_pic_url = fs.url(filename)
        else:
            logo_pic_url = None

        try:
            company = Companies.objects.get(id=request.user.managers.company_id_id)

            company.name = company_name

            if logo_pic_url != None:
                company.logo = logo_pic_url
            company.save()

            messages.success(request, "Profil firmy został zaktualizowany")
            return HttpResponseRedirect(reverse("manager_profile"))
        except:
            messages.error(request, "Aktualizacja profilu firmy nieudana")
            return HttpResponseRedirect(reverse("manager_profile"))


def manager_change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Zmian hasła zakończona sukcesem')
            return redirect('manager_profile')
    else:
        form = ChangePasswordForm(request.user)

    return render(request, "manager_template/change_password_template.html", {"form": form})