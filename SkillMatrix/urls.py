"""SkillMatrix URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from SkillMatrix import settings
from skill_matrix_app import views, AdminViews, ManagerViews, AssistantViews

urlpatterns = [

    path('showDemoPage', views.showDemoPage, name="showDemoPage"),
    path('signup_admin', views.signup_admin, name="signup_admin"),
    path('signup_manager', views.signup_manager, name="signup_manager"),

    path('do_admin_signup', views.do_admin_signup, name="do_admin_signup"),
    path('do_manager_signup', views.do_manager_signup, name="do_manager_signup"),

    path('accounts/', include('django.contrib.auth.urls')),



    path('admin/', admin.site.urls),

    path('', views.ShowLoginPage, name="show_login"),
    path('get_user_details', views.GetUserDetails),
    path('logout_user', views.logout_user, name="logout_user"),
    path('doLogin', views.doLogin, name="do_login"),

    path('admin_home', AdminViews.admin_home, name="admin_home"),
    path('admin_profile', AdminViews.admin_profile, name="admin_profile"),
    path('admin_profile_save', AdminViews.admin_profile_save, name="admin_profile_save"),
    path('admin_change_password', AdminViews.admin_change_password, name="admin_change_password"),


    path('add_admin', AdminViews.add_admin, name="add_admin"),
    path('add_admin_save', AdminViews.add_admin_save, name="add_admin_save"),
    path('manage_admin', AdminViews.manage_admin, name="manage_admin"),
    path('delete_admin/<str:admin_id>', AdminViews.delete_admin, name="delete_admin"),
    path('check_email_exist', AdminViews.check_email_exist, name="check_email_exist"),

    path('manage_users', AdminViews.manage_users, name="manage_users"),

    path('add_manager', AdminViews.add_manager, name="add_manager"),
    path('add_manager_save', AdminViews.add_manager_save, name="add_manager_save"),


    #path('add_assistant', AdminViews.add_assistant, name="add_assistant"),



    path('manager_home', ManagerViews.manager_home, name="manager_home"),
    path('manager_profile', ManagerViews.manager_profile, name="manager_profile"),
    path('manager_profile_save', ManagerViews.manager_profile_save, name="manager_profile_save"),
    path('manager_company_save', ManagerViews.manager_company_save, name="manager_company_save"),
    path('manager_change_password', ManagerViews.manager_change_password, name="manager_change_password"),

    path('add_assistant', ManagerViews.add_assistant, name="add_assistant"),
    path('add_assistant_save', ManagerViews.add_assistant_save, name="add_assistant_save"),
    path('manage_assistant', ManagerViews.manage_assistant, name="manage_assistant"),
    path('delete_assistant/<str:assistant_id>', ManagerViews.delete_assistant, name="delete_assistant"),

    path('add_worker', ManagerViews.add_worker, name="add_worker"),
    path('add_worker_save', ManagerViews.add_worker_save, name="add_worker_save"),
    path('manage_worker', ManagerViews.manage_worker, name="manage_worker"),
    path('delete_worker/<str:worker_id>', ManagerViews.delete_worker, name="delete_worker"),
    path('edit_worker/<str:worker_id>', ManagerViews.edit_worker, name="edit_worker"),
    path('edit_worker_save', ManagerViews.edit_worker_save, name="edit_worker_save"),
    path('profile_worker/<str:worker_id>', ManagerViews.profile_worker, name="profile_worker"),

    path('manage_position', ManagerViews.manage_position, name="manage_position"),
    path('add_position_save', ManagerViews.add_position_save, name="add_position_save"),
    path('delete_position/<str:position_id>', ManagerViews.delete_position, name="delete_position"),
    path('unpin_from_position/<str:worker_id>', ManagerViews.unpin_from_position, name="unpin_from_position"),
    path('edit_position_save', ManagerViews.edit_position_save, name="edit_position_save"),
    path('pin_to_position', ManagerViews.pin_to_position, name="pin_to_position"),


    path('manage_division', ManagerViews.manage_division, name="manage_division"),
    path('add_division_save', ManagerViews.add_division_save, name="add_division_save"),
    path('delete_division/<str:division_id>', ManagerViews.delete_division, name="delete_division"),
    path('unpin_from_division/<str:worker_id>', ManagerViews.unpin_from_division, name="unpin_from_division"),
    path('edit_division_save', ManagerViews.edit_division_save, name="edit_division_save"),
    path('pin_to_division', ManagerViews.pin_to_division, name="pin_to_division"),


    path('manage_skill', ManagerViews.manage_skill, name="manage_skill"),
    path('add_skill_save', ManagerViews.add_skill_save, name="add_skill_save"),
    path('delete_skill/<str:skill_id>', ManagerViews.delete_skill, name="delete_skill"),
    path('edit_skill_save', ManagerViews.edit_skill_save, name="edit_skill_save"),




    path('edit_rating_worker_skill/<str:worker_id>', ManagerViews.edit_rating_worker_skill, name="edit_rating_worker_skill"),
    path('edit_rating_worker_skill_save', ManagerViews.edit_rating_worker_skill_save, name="edit_rating_worker_skill_save"),
    path('skill_matrix_table', ManagerViews.skill_matrix_table, name="skill_matrix_table"),
    path('comparison_of_workers', ManagerViews.comparison_of_workers, name="comparison_of_workers"),
    path('compare_workers', ManagerViews.compare_workers, name="compare_workers"),


















    path('assistant_home', AssistantViews.assistant_home, name="assistant_home"),
    path('assistant_profile', AssistantViews.assistant_profile, name="assistant_profile"),
    path('assistant_profile_save', AssistantViews.assistant_profile_save, name="assistant_profile_save"),
    path('assistant_change_password', AssistantViews.assistant_change_password, name="assistant_change_password"),

              ]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
