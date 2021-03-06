from .utils import get_plot
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from skill_matrix_app.forms import ChangePasswordForm, CreateUserForm
from skill_matrix_app.models import CustomUser, Companies, Managers, Assistants, Workers, Positions, Divisions, Skills, \
    Ratings, Totals
from skill_matrix_app.views import send_activation_email


def manager_home(request):
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    workers_count = Workers.objects.filter(company_id=company.id).count()
    positions_count = Positions.objects.filter(company_id=company.id).count()
    divisions_count = Divisions.objects.filter(company_id=company.id).count()
    skills_count = Skills.objects.filter(company_id=company.id).count()

    positions = Positions.objects.filter(company_id=company.id)
    worker_count_list_in_position = []
    for position in positions:
        workers_position_count = Workers.objects.filter(position_id=position.id).count()
        worker_count_list_in_position.append(workers_position_count)

    divisions = Divisions.objects.filter(company_id=company.id)
    worker_count_list_in_division = []
    for division in divisions:
        workers = Workers.objects.filter(division_id=division.id).count()
        worker_count_list_in_division.append(workers)

    worker_rating_list = []
    workers = Workers.objects.filter(company_id=company.id)
    for worker in workers:
        worker_rate = Ratings.objects.filter(worker_id=worker.id).aggregate(Sum('rate'))
        worker_rating_list.append(worker_rate['rate__sum'])


    context = {"company": company, "workers_count": workers_count, "positions_count": positions_count,
               "divisions_count": divisions_count, "skills_count": skills_count, "positions": positions,
               "divisions": divisions, "workers": workers,
               "worker_count_list_in_position": worker_count_list_in_position,
               "worker_count_list_in_division": worker_count_list_in_division,
               "worker_rating_list": worker_rating_list}

    return render(request, 'manager_template/home_content.html', context)


def add_assistant(request):
    form = CreateUserForm()

    return render(request, 'manager_template/add_assistant_template.html', {"form": form})


def manage_assistant(request):
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    assistants = Assistants.objects.filter(company_id=company.id)
    form = CreateUserForm()

    return render(request, "manager_template/manage_assistant_template.html", {"assistants": assistants, "form": form})


def delete_assistant(request, assistant_id):
    user = CustomUser.objects.get(id=assistant_id)

    if (user.assistants.company_id.id == request.user.managers.company_id_id):
        user.delete()
        messages.success(request, "Profil zosta?? usuni??ty")
        return HttpResponseRedirect(reverse("manage_assistant"))
    else:
        messages.error(request, "Usuni??cie profilu nieudana")
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
            user = CustomUser.objects.create_user(username=email, email=email, last_name=last_name,
                                                  first_name=first_name, user_type=3)
            user.set_password(CustomUser.objects.make_random_password())
            user.assistants.company_id_id = company.id
            user.save()

            send_activation_email(request, user)

            messages.success(request, "Dodanie u??ytkownika zako??czone powodzeniem")
            return HttpResponseRedirect(reverse("manage_assistant"))
        else:
            form = CreateUserForm(request.POST)
            messages.error(request, "Dodanie u??ytkownika zako??czone niepowodzeniem")
            return render(request, 'manager_template/add_assistant_template.html', {"form": form})


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

            messages.success(request, "Profil zosta?? zaktualizowany")
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

            messages.success(request, "Profil firmy zosta?? zaktualizowany")
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
            messages.success(request, 'Zmian has??a zako??czona sukcesem')
            return redirect('manager_profile')
    else:
        form = ChangePasswordForm(request.user)

    return render(request, "manager_template/change_password_template.html", {"form": form})


def add_worker(request):
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    positions = Positions.objects.filter(company_id=company.id)
    divisions = Divisions.objects.filter(company_id=company.id)

    return render(request, 'manager_template/add_worker_template.html',
                  {"positions": positions, "divisions": divisions})


def add_worker_save(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    else:
        first_name = request.POST.get('first_name')
        second_name = request.POST.get('second_name')
        last_name = request.POST.get('last_name')
        birthday = request.POST.get('birthday')
        archival = request.POST.get('archival')
        position_id = request.POST.get('position')
        division_id = request.POST.get('division')

        if position_id == "0":
            position_id = None

        if division_id == "0":
            division_id = None

        if archival == None:
            archival = False
        else:
            archival = True

        if request.FILES.get('profile_pic', False):
            profile_pic = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)
        else:
            profile_pic_url = None

        try:
            company = Companies.objects.get(id=request.user.managers.company_id_id)
            worker_model = Workers(first_name=first_name, second_name=second_name, last_name=last_name,
                                   birthday=birthday, archival=archival, position_id_id=position_id,
                                   division_id_id=division_id)
            worker_model.company_id_id = company.id
            if profile_pic_url != None:
                worker_model.profile_pic = profile_pic_url
            worker_model.save()
            skills = Skills.objects.filter(company_id=company.id)
            for skill in skills:
                rating = Ratings(skill_id_id=skill.id, worker_id_id=worker_model.id, company_id_id=company.id)
                rating.save()
            total = Totals(worker_id_id=worker_model.id, company_id_id=company.id)
            total.save()

            messages.success(request, "Dodanie u??ytkownika zako??czone powodzeniem")
            return HttpResponseRedirect(reverse("manage_worker"))
        except:
            messages.error(request, "Dodanie u??ytkownika zako??czone niepowodzeniem")
            return HttpResponseRedirect(request("add_worker"))


def manage_worker(request):
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    workers = Workers.objects.filter(company_id=company.id).exclude(archival=True)
    archivals = Workers.objects.filter(company_id=company.id).exclude(archival=False)
    return render(request, "manager_template/manage_worker_template.html", {"workers": workers, "archivals": archivals})


def delete_worker(request, worker_id):
    worker = Workers.objects.get(id=worker_id)
    if (worker.company_id.id == request.user.managers.company_id_id):
        worker.delete()
        messages.success(request, "Pracownik zosta?? usuni??ty")
        return HttpResponseRedirect(reverse("manage_worker"))
    else:
        messages.error(request, "Usuni??cie pracownika nieudane")
        return HttpResponseRedirect(reverse("manage_worker"))


def edit_worker(request, worker_id):
    try:
        request.session['worker_id'] = worker_id
        worker = Workers.objects.get(id=worker_id)
        if (worker.company_id.id == request.user.managers.company_id_id):
            company = Companies.objects.get(id=request.user.managers.company_id_id)
            positions = Positions.objects.filter(company_id=company.id)
            divisions = Divisions.objects.filter(company_id=company.id)
            return render(request, "manager_template/edit_worker_template.html",
                          {"worker": worker, "worker_id": worker_id, "positions": positions, "divisions": divisions})
        else:
            return HttpResponseRedirect(reverse("manage_worker"))
    except:
        return HttpResponseRedirect(reverse("manage_worker"))


def edit_worker_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        worker_id = request.session.get("worker_id")
        if worker_id is None:
            return HttpResponseRedirect(reverse("manage_worker"))

        first_name = request.POST.get('first_name')
        second_name = request.POST.get('second_name')
        last_name = request.POST.get('last_name')
        birthday = request.POST.get('birthday')
        archival = request.POST.get('archival')
        position_id = request.POST.get('position')
        division_id = request.POST.get('division')

        if position_id == "0":
            position_id = None

        if division_id == "0":
            division_id = None

        if archival is None:
            archival = False
        else:
            archival = True

        if request.FILES.get('profile_pic', False):
            profile_pic = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)
        else:
            profile_pic_url = None

        try:
            worker_model = Workers.objects.get(id=worker_id)
            worker_model.first_name = first_name
            worker_model.second_name = second_name
            worker_model.last_name = last_name
            worker_model.birthday = birthday
            worker_model.archival = archival
            worker_model.position_id_id = position_id
            worker_model.division_id_id = division_id
            if profile_pic_url != None:
                worker_model.profile_pic = profile_pic_url
            worker_model.save()
            del request.session['worker_id']

            messages.success(request, "Edycja pracownika zako??czone powodzeniem")
            return HttpResponseRedirect(reverse("manage_worker"))
        except:
            messages.error(request, "Edycja pracownika zako??czone niepowodzeniem")
            return render(request, 'manager_template/edit_worker_template.html')


def profile_worker(request, worker_id):
    try:
        worker = Workers.objects.get(id=worker_id)
        if (worker.company_id.id == request.user.managers.company_id_id):
            ratings = Ratings.objects.filter(worker_id=worker.id)
            worker_ratings = Ratings.objects.filter(worker_id=worker.id)
            worker_count = worker_ratings.aggregate(Count('rate'))
            worker_sum = worker_ratings.aggregate(Sum('rate'))

            worker_rate = int(worker_sum['rate__sum'] / (worker_count['rate__count'] * 4) * 100)

            qs = Totals.objects.filter(worker_id=worker_id)
            x = [x.created_at for x in qs]
            y = [y.total_rate for y in qs]
            chart = get_plot(x, y)

            context = {"worker": worker, "worker_id": worker_id, "ratings": ratings, "worker_rate": worker_rate,
                       "chart": chart}
            return render(request, "manager_template/profile_worker_template.html", context)
        else:
            return HttpResponseRedirect(reverse("manage_worker"))
    except:
        return HttpResponseRedirect(reverse("manage_worker"))


def manage_position(request):
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    positions = Positions.objects.filter(company_id=company.id)
    workers = Workers.objects.filter(company_id=company.id).order_by('last_name').exclude(archival=True)

    return render(request, "manager_template/manage_position_template.html",
                  {"positions": positions, "workers": workers})


def add_position_save(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    else:
        name = request.POST.get('name')
        try:
            company = Companies.objects.get(id=request.user.managers.company_id_id)
            position_model = Positions(name=name, company_id_id=company.id)
            position_model.save()

            messages.success(request, "Dodanie stanowiska zako??czone powodzeniem")
            return HttpResponseRedirect(reverse("manage_position"))
        except:
            messages.error(request, "Dodanie stanowiska zako??czone niepowodzeniem")
            return HttpResponseRedirect(request("manage_position"))


def delete_position(request, position_id):
    try:
        position = Positions.objects.get(id=position_id)
        if (position.company_id.id == request.user.managers.company_id_id):
            position.delete()
            messages.success(request, "Stanowisko zosta??o usuni??te")
            return HttpResponseRedirect(reverse("manage_position"))
        else:
            messages.error(request, "Usuni??cie stanowiska nieudane")
            return HttpResponseRedirect(reverse("manage_position"))
    except:
        messages.error(request, "Usuni??cie stanowiska nieudane. Najpierw odepnij pracownik??w")
        return HttpResponseRedirect(reverse("manage_position"))


def unpin_from_position(request, worker_id):
    try:
        worker = Workers.objects.get(id=worker_id)
        if (worker.company_id.id == request.user.managers.company_id_id):
            worker.position_id_id = None
            worker.save()
            messages.success(request, "Pracownik zosta?? pomy??lnie odpi??ty")
            return HttpResponseRedirect(reverse("manage_position"))
        else:
            messages.error(request, "Odpi??cie pracownika nieudane")
            return HttpResponseRedirect(reverse("manage_position"))
    except:
        messages.error(request, "Odpi??cie pracownika nieudane")
        return HttpResponseRedirect(reverse("manage_position"))


def edit_position_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        position_id = request.POST.get('id')
        name = request.POST.get('name')

        try:
            position = Positions.objects.get(id=position_id)
            if (position.company_id.id == request.user.managers.company_id_id):
                try:
                    position.name = name
                    position.save()
                    messages.success(request, "Nazwa stanowiska zosta??a zmieniona")
                    return HttpResponseRedirect(reverse("manage_position"))
                except:
                    messages.error(request, "Nazwa stanowiska nie zosta??a zmieniona")
                    return HttpResponseRedirect(reverse("manage_position"))
            else:
                messages.error(request, "Nazwa stanowiska nie zosta??a zmieniona")
                return HttpResponseRedirect(reverse("manage_position"))
        except:
            messages.error(request, "Nazwa stanowiska nie zosta??a zmieniona")
            return HttpResponseRedirect(reverse("manage_position"))


def pin_to_position(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        worker_id = request.POST.get('worker_id')
        position_id = request.POST.get('id')
        try:
            worker = Workers.objects.get(id=worker_id)
            position = Positions.objects.get(id=position_id)
            if (
                    position.company_id.id == request.user.managers.company_id_id & worker.company_id.id == request.user.managers.company_id_id):
                try:
                    worker.position_id_id = position_id
                    worker.save()
                    messages.success(request, "Pracownik zosta?? przypi??ty")
                    return HttpResponseRedirect(reverse("manage_position"))
                except:
                    messages.error(request, "Przypi??cie pracownika nieudane")
                    return HttpResponseRedirect(reverse("manage_position"))
            else:
                messages.error(request, "Przypi??cie pracownika nieudane")
                return HttpResponseRedirect(reverse("manage_position"))
        except:
            messages.error(request, "Przypi??cie pracownika nieudane")
            return HttpResponseRedirect(reverse("manage_position"))


def manage_division(request):
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    divisions = Divisions.objects.filter(company_id=company.id)
    workers = Workers.objects.filter(company_id=company.id).order_by('last_name').exclude(archival=True)

    return render(request, "manager_template/manage_division_template.html",
                  {"divisions": divisions, "workers": workers})


def add_division_save(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    else:
        name = request.POST.get('name')
        try:
            company = Companies.objects.get(id=request.user.managers.company_id_id)
            division_model = Divisions(name=name, company_id_id=company.id)
            division_model.save()

            messages.success(request, "Dodanie dzia??u zako??czone powodzeniem")
            return HttpResponseRedirect(reverse("manage_division"))
        except:
            messages.error(request, "Dodanie dzia??u zako??czone niepowodzeniem")
            return HttpResponseRedirect(request("manage_division"))


def delete_division(request, division_id):
    try:
        division = Divisions.objects.get(id=division_id)
        if (division.company_id.id == request.user.managers.company_id_id):
            division.delete()
            messages.success(request, "Dzia?? zosta?? usuni??ty")
            return HttpResponseRedirect(reverse("manage_division"))
        else:
            messages.error(request, "Usuni??cie dzia??u nieudane")
            return HttpResponseRedirect(reverse("manage_division"))
    except:
        messages.error(request, "Usuni??cie dzia??u nieudane. Najpierw odepnij pracownik??w")
        return HttpResponseRedirect(reverse("manage_division"))


def unpin_from_division(request, worker_id):
    try:
        worker = Workers.objects.get(id=worker_id)
        if (worker.company_id.id == request.user.managers.company_id_id):
            worker.division_id_id = None
            worker.save()
            messages.success(request, "Pracownik zosta?? pomy??lnie odpi??ty")
            return HttpResponseRedirect(reverse("manage_division"))
        else:
            messages.error(request, "Odpi??cie pracownika nieudane")
            return HttpResponseRedirect(reverse("manage_division"))
    except:
        messages.error(request, "Odpi??cie pracownika nieudane")
        return HttpResponseRedirect(reverse("manage_division"))


def edit_division_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        division_id = request.POST.get('id')
        name = request.POST.get('name')

        try:
            division = Divisions.objects.get(id=division_id)
            if (division.company_id.id == request.user.managers.company_id_id):
                try:
                    division.name = name
                    division.save()
                    messages.success(request, "Nazwa dzia??u zosta??a zmieniona")
                    return HttpResponseRedirect(reverse("manage_division"))
                except:
                    messages.error(request, "Nazwa dzia??u nie zosta??a zmieniona")
                    return HttpResponseRedirect(reverse("manage_division"))
            else:
                messages.error(request, "Nazwa dzia??u nie zosta??a zmieniona")
                return HttpResponseRedirect(reverse("manage_division"))
        except:
            messages.error(request, "Nazwa dzia??u nie zosta??a zmieniona")
            return HttpResponseRedirect(reverse("manage_division"))


def pin_to_division(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        worker_id = request.POST.get('worker_id')
        division_id = request.POST.get('id')
        try:
            worker = Workers.objects.get(id=worker_id)
            division = Divisions.objects.get(id=division_id)
            if (
                    division.company_id.id == request.user.managers.company_id_id & worker.company_id.id == request.user.managers.company_id_id):
                try:
                    worker.division_id_id = division_id
                    worker.save()
                    messages.success(request, "Pracownik zosta?? przypi??ty")
                    return HttpResponseRedirect(reverse("manage_division"))
                except:
                    messages.error(request, "Przypi??cie pracownika nieudane")
                    return HttpResponseRedirect(reverse("manage_division"))
            else:
                messages.error(request, "Przypi??cie pracownika nieudane")
                return HttpResponseRedirect(reverse("manage_division"))
        except:
            messages.error(request, "Przypi??cie pracownika nieudane")
            return HttpResponseRedirect(reverse("manage_division"))


def manage_skill(request):
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    skills = Skills.objects.filter(company_id=company.id)

    return render(request, "manager_template/manage_skill_template.html", {"skills": skills})


def add_skill_save(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    else:
        name = request.POST.get('name')
        try:
            company = Companies.objects.get(id=request.user.managers.company_id_id)

            skill_model = Skills(name=name, company_id_id=company.id)
            skill_model.save()
            workers = Workers.objects.filter(company_id=company.id)

            for worker in workers:
                rating = Ratings(skill_id_id=skill_model.id, worker_id_id=worker.id, company_id_id=company.id)
                rating.save()
                worker_count = Totals.objects.filter(worker_id=worker.id).aggregate(Count('worker_id_id'))
                if worker_count['worker_id_id__count'] == 0:
                    total = Totals(worker_id_id=worker.id, company_id_id=company.id, total_rate=0)
                    total.save()

            messages.success(request, "Dodanie umiej??tno??ci zako??czone powodzeniem")
            return HttpResponseRedirect(reverse("manage_skill"))
        except:
            messages.error(request, "Dodanie umiej??tno??ci zako??czone niepowodzeniem")
            return HttpResponseRedirect(request("manage_skill"))


def delete_skill(request, skill_id):
    try:
        skill = Skills.objects.get(id=skill_id)
        if (skill.company_id.id == request.user.managers.company_id_id):

            skill.delete()
            workers = Workers.objects.filter(company_id=skill.company_id.id)
            for worker in workers:
                worker_sum = Ratings.objects.filter(worker_id=worker.id).aggregate(Sum('rate'))
                total = Totals(worker_id_id=worker.id, company_id_id=skill.company_id.id,
                               total_rate=worker_sum['rate__sum'])
                total.save()

            messages.success(request, "Umiej??tno???? zosta??a usuni??ta")
            return HttpResponseRedirect(reverse("manage_skill"))
        else:
            messages.error(request, "Usuni??cie umiej??tno??ci nieudane")
            return HttpResponseRedirect(reverse("manage_skill"))
    except:
        messages.error(request, "Usuni??cie umiej??tno??ci nieudane.")
        return HttpResponseRedirect(reverse("manage_skill"))


def edit_skill_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        skill_id = request.POST.get('id')
        name = request.POST.get('name')

        try:
            skill = Skills.objects.get(id=skill_id)
            if (skill.company_id.id == request.user.managers.company_id_id):
                try:
                    skill.name = name
                    skill.save()
                    messages.success(request, "Nazwa umiej??tno??ci zosta??a zmieniona")
                    return HttpResponseRedirect(reverse("manage_skill"))
                except:
                    messages.error(request, "Nazwa umiej??tno??ci nie zosta??a zmieniona")
                    return HttpResponseRedirect(reverse("manage_skill"))
            else:
                messages.error(request, "Nazwa umiej??tno??ci nie zosta??a zmieniona")
                return HttpResponseRedirect(reverse("manage_skill"))
        except:
            messages.error(request, "Nazwa umiej??tno??ci nie zosta??a zmieniona")
            return HttpResponseRedirect(reverse("manage_skill"))


def edit_rating_worker_skill(request, worker_id):
    try:
        request.session['worker_id'] = worker_id
        company = Companies.objects.get(id=request.user.managers.company_id_id)
        worker = Workers.objects.get(id=worker_id)
        if (worker.company_id.id == request.user.managers.company_id_id):
            ratings = Ratings.objects.filter(worker_id=worker.id)
            skills = Skills.objects.filter(company_id=company.id)
            list = []
            for i in range(5):
                list.append(i)
            return render(request, "manager_template/edit_rating_worker_skill_template.html",
                          {"skills": skills, "ratings": ratings, "worker": worker, "worker_id": worker_id,
                           "list": list})
    except:
        return HttpResponseRedirect(reverse("manage_worker"))


def edit_rating_worker_skill_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        worker_id = request.session.get("worker_id")
        if worker_id is None:
            return HttpResponseRedirect(reverse("manage_worker"))
        try:

            ratings = Ratings.objects.filter(worker_id_id=worker_id)
            for rating in ratings:
                rate = int(request.POST.get(str(rating.id)))
                if rate >= 0 and rate < 5:
                    worker_rating = Ratings.objects.get(id=rating.id)
                    worker_rating.rate = rate
                    worker_rating.save()

            company = Companies.objects.get(id=request.user.managers.company_id_id)

            worker_sum = Ratings.objects.filter(worker_id=worker_id).aggregate(Sum('rate'))
            total = Totals(worker_id_id=worker_id, company_id_id=company.id, total_rate=worker_sum['rate__sum'])
            total.save()

            del request.session['worker_id']
            messages.success(request, "Oceny zosta??y zmienione")
            return HttpResponseRedirect(reverse("edit_rating_worker_skill", kwargs={'worker_id': worker_id}))
        except:
            messages.error(request, "Oceny nie zosta??y zmienione")
            return HttpResponseRedirect(reverse("edit_rating_worker_skill", kwargs={'worker_id': worker_id}))


def skill_matrix_table(request):
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    workers = Workers.objects.filter(company_id=company.id).exclude(archival=True).order_by('position_id')
    skills = Skills.objects.filter(company_id=company.id)
    ratings = Ratings.objects.filter(company_id=company.id).exclude(worker_id__archival=True)
    count_position = len(Workers.objects.filter(company_id=company.id).exclude(position_id__isnull=True))
    count_division = len(Workers.objects.filter(company_id=company.id).exclude(division_id__isnull=True))

    context = {"ratings": ratings, "skills": skills, "workers": workers, "count_position": count_position,
               "count_division": count_division}

    return render(request, "manager_template/skill_matrix_table_template.html", context)


def comparison_of_workers(request):
    company = Companies.objects.get(id=request.user.managers.company_id_id)
    workers = Workers.objects.filter(company_id=company.id).exclude(archival=True)
    return render(request, "manager_template/comparision_of_workers_template.html", {"workers": workers})


def compare_workers(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    else:
        worker_1 = request.POST.get('worker_1')
        worker_2 = request.POST.get('worker_2')

        try:
            worker1 = Workers.objects.get(id=worker_1)
            worker2 = Workers.objects.get(id=worker_2)
            if (
                    worker1.company_id.id == request.user.managers.company_id_id and worker2.company_id.id == request.user.managers.company_id_id):
                company = Companies.objects.get(id=request.user.managers.company_id_id)
                workers = Workers.objects.filter(company_id=company.id).exclude(archival=True)
                skills = Skills.objects.filter(company_id=company.id)

                worker_ratings1 = Ratings.objects.filter(worker_id=worker1.id)
                worker_ratings2 = Ratings.objects.filter(worker_id=worker2.id)
                worker1_count = worker_ratings1.aggregate(Count('rate'))
                worker1_sum = worker_ratings1.aggregate(Sum('rate'))
                worker2_count = worker_ratings2.aggregate(Count('rate'))
                worker2_sum = worker_ratings2.aggregate(Sum('rate'))
                worker1_rate = int(worker1_sum['rate__sum'] / (worker1_count['rate__count'] * 4) * 100)

                worker2_rate = int(worker2_sum['rate__sum'] / (worker2_count['rate__count'] * 4) * 100)
                numbers = [0, 1, 2, 3, 4]
                rowspan = 0
                if worker1.position_id or worker2.position_id:
                    if worker1.division_id or worker2.division_id:
                        rowspan = 5
                    elif not worker1.division_id and not worker2.division_id:
                        rowspan = 4
                elif not worker1.position_id and not worker2.position_id:
                    if worker1.division_id or worker2.division_id:
                        rowspan = 4
                    elif not worker1.division_id and not worker2.division_id:
                        rowspan = 3

                context = {"workers": workers, "worker1": worker1, "worker2": worker2, "skills": skills,
                           "worker1_rate": worker1_rate, "worker2_rate": worker2_rate,
                           "worker_ratings1": worker_ratings1, "worker_ratings2": worker_ratings2, "numbers": numbers,
                           "rowspan": rowspan}

                return render(request, "manager_template/comparision_of_workers_template.html", context)
            else:
                return HttpResponseRedirect(reverse("comparision_of_workers"))
        except:
            return HttpResponseRedirect(reverse("comparision_of_workers"))
