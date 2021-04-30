from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from skill_matrix_app.forms import ChangePasswordForm
from skill_matrix_app.models import Companies, CustomUser, Assistants


def assistant_home(request):
    print(request.user.id)
    print(request.user.assistants.company_id_id)
    company = Companies.objects.get(id=request.user.assistants.company_id_id)
    print(company.name)
    print(company.id)

    return render(request, 'assistant_template/home_content.html', {"company": company})



def assistant_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, "assistant_template/assistant_profile_template.html", {"user": user})

def assistant_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse(assistant_profile))
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
            user_profile = Assistants.objects.get(admin=request.user.id)
            if profile_pic_url != None:
                user_profile.profile_pic = profile_pic_url
            print(user_profile)
            user_profile.save()

            messages.success(request, "Profil został zaktualizowany")
            return HttpResponseRedirect(reverse("assistant_profile"))
        except:
            messages.error(request, "Aktualizacja profilu nieudana")
            return HttpResponseRedirect(reverse("assistant_profile"))


def assistant_change_password(request):
    # passw = CustomUser.objects.get(password=request.user.password)
    # print(passw)
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Zmian hasła zakończona sukcesem')
            return redirect('assistant_profile')
    else:
        form = ChangePasswordForm(request.user)

    return render(request, "assistant_template/change_password_template.html", {"form": form})