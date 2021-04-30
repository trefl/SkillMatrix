from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class LoginCheckMiddleWare(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        module_name = view_func.__module__
        user = request.user
        if user.is_authenticated:
            if user.user_type == "1":
                if module_name == "skill_matrix_app.AdminViews":
                    pass
                elif module_name == "skill_matrix_app.views" or module_name == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse("admin_home"))
            elif user.user_type == "2":
                if module_name == "skill_matrix_app.ManagerViews":
                    pass
                elif module_name == "skill_matrix_app.views" or module_name == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse("manager_home"))
            elif user.user_type == "3":
                if module_name == "skill_matrix_app.AssistantViews" or module_name == "django.views.static":
                    pass
                elif module_name == "skill_matrix_app.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("assistant_home"))
            else:
                return HttpResponseRedirect(reverse("show_login"))



        else:
            if request.path == reverse("show_login") \
                    or request.path == reverse("do_login") \
                    or request.path == reverse("signup_manager") \
                    or request.path == reverse("do_admin_signup") \
                    or request.path == reverse("do_manager_signup") \
                    or request.path == reverse("signup_admin") \
                    or module_name == "django.contrib.auth.views":
                pass
            else:
                return HttpResponseRedirect(reverse("show_login"))






