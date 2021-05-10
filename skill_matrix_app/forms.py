from datetime import date
from re import search

import self as self
from phone_field import PhoneField
from crispy_forms import bootstrap, layout
from crispy_forms.bootstrap import PrependedText, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Submit
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import validate_email
from django.forms import DateField

from django.urls import reverse
from django.utils.datetime_safe import datetime
from urllib3 import request

from skill_matrix_app.models import CustomUser, Workers, Positions, Companies


class CreateUserForm(forms.Form):
    first_name = forms.CharField(label="Imię", max_length=50, widget=forms.TextInput(
        attrs={"class": "form-control", "autocomplete": "off", "placeholder": "Podaj imię"}))
    last_name = forms.CharField(label="Nazwisko", required=False, max_length=50, widget=forms.TextInput(
        attrs={"class": "form-control", "autocomplete": "off", "placeholder": "Podaj nazwisko"}))
    email = forms.EmailField(label="Email", required=True, max_length=50, widget=forms.EmailInput(
        attrs={"class": "form-control", "autocomplete": "off", "placeholder": "Podaj email"}),
                             error_messages={'invalid': "Nieprawidłowy email"})

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email jest już zajęty")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = layout.Layout(
            layout.Div(
                bootstrap.AppendedText('first_name', '<i class="fas fa-user"></i>'),
                bootstrap.AppendedText('last_name', '<i class="fas fa-user"></i>'),
                bootstrap.AppendedText('email', '<i class="fas fa-envelope"></i>'),

            ),
            Submit('sign_up', 'Zaproś', css_class="btn btn-lg btn-info btn-block"),

        )


class SignupManagerForm(forms.Form):
    first_name = forms.CharField(label="Imię", required=True, max_length=50, widget=forms.TextInput(
        attrs={"class": "form-control", "autocomplete": "off", "placeholder": "Podaj imię"}))
    last_name = forms.CharField(label="Nazwisko", required=True, max_length=50, widget=forms.TextInput(
        attrs={"class": "form-control", "autocomplete": "off", "placeholder": "Podaj nazwisko"}))
    company = forms.CharField(label="Firma", required=True, max_length=50, widget=forms.TextInput(
        attrs={"class": "form-control", "autocomplete": "off", "placeholder": "Podaj nazwę firmy"}))
    email = forms.EmailField(label="Email", required=True, max_length=50, widget=forms.EmailInput(
        attrs={"class": "form-control", "autocomplete": "off", "placeholder": "Podaj email"}),
                             error_messages={'invalid': "Nieprawidłowy email"})
    password = forms.CharField(label="Hasło", required=True, max_length=50, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Podaj hasło"}),
                               error_messages={'invalid': "Nieprawidłowe hasło"})
    confirm_password = forms.CharField(label="Hasło", required=True, max_length=50, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Powtórz hasło"}),
                                       error_messages={'invalid': "Nieprawidłowe hasło"})

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email jest już zajęty")

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        minLength = 8
        textError = f'Hasło powinno składać się z minimum {minLength} znaków, przynajmniej jednej dużej litery oraz cyfry'
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Hasła nie pasują do siebie")
        if len(password) < minLength:
            raise forms.ValidationError(textError)
        if search('[0-9]', password) is None:
            raise forms.ValidationError(textError)
        if search('[A-Z]', password) is None:
            raise forms.ValidationError(textError)
        if search('[a-z]', password) is None:
            raise forms.ValidationError(textError)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = layout.Layout(
            layout.Div(
                bootstrap.AppendedText('first_name', '<i class="fas fa-user"></i>'),
                bootstrap.AppendedText('last_name', '<i class="fas fa-user"></i>'),
                bootstrap.AppendedText('company', '<i class="fas fa-users"></i>'),
                bootstrap.AppendedText('email', '<i class="fas fa-envelope"></i>'),
                bootstrap.AppendedText('password', '<i class="fas fa-lock"></i>'),
                bootstrap.AppendedText('confirm_password', '<i class="fas fa-lock"></i>'),

            ),
            Submit('sign_up', 'Zarejestruj', css_class="btn btn-lg btn-info btn-block"),

        )


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label="Stare hasło", required=True, max_length=50, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Podaj stare hasło"}))
    new_password1 = forms.CharField(label="Nowe hasło", required=True, max_length=50, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Podaj nowe hasło"}))
    new_password2 = forms.CharField(label="Nowe hasło", required=True, max_length=50, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Potwierdź nowe hasło"}))

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        print(self.user.check_password)
        if self.user.check_password == old_password:
            print(old_password)
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Nieprawidłowe hasło")

    def clean_new_password2(self):
        password = self.cleaned_data['new_password1']
        confirm_password = self.cleaned_data['new_password2']

        minLength = 8
        textError = f'Hasło powinno składać się z minimum {minLength} znaków, przynajmniej jednej dużej litery oraz cyfry'
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Hasła nie pasują do siebie")
        if len(password) < minLength:
            raise forms.ValidationError(textError)
        if search('[0-9]', password) is None:
            raise forms.ValidationError(textError)
        if search('[A-Z]', password) is None:
            raise forms.ValidationError(textError)
        if search('[a-z]', password) is None:
            raise forms.ValidationError(textError)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        Submit('change_password', 'Zmień hasło', css_class="btn btn-lg btn-primary btn-block"),

class DateInput(forms.DateInput):
    input_type = 'date'


class CreateWorkerForm(forms.Form):
    first_name = forms.CharField(label="Imię", required=True, max_length=50,
                                 widget=forms.TextInput(attrs={"class": "form-control"}))
    second_name = forms.CharField(label="Drugie imię", required=False, max_length=50,
                                  widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label="Nazwisko", required=True, max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
    birthday = forms.DateField(label="Data urodzenia", initial=date.today, widget=DateInput)
    profile_pic = forms.FileField(label="Zdjęcie", required=False, max_length=50, widget=forms.FileInput(
        attrs={"class": "form-control-file", "accept": ".jpg,.gif,.png"}))
    archival = forms.BooleanField(label="Archiwalny", required=False)
    position_id = forms.ChoiceField(label="Stanowisko", required=False,
                                    widget=forms.Select(attrs={"class": "form-control"}))
    division_id = forms.ChoiceField(label="Dział/Brygada", required=False,
                                    widget=forms.Select(attrs={"class": "form-control"}))












# class EditUserForm(forms.Form):
#     first_name = forms.CharField(label="Imię", max_length=50, widget=forms.TextInput(
#         attrs={"class": "form-control", "autocomplete": "off", "placeholder": "Podaj imię"}))
#     last_name = forms.CharField(label="Nazwisko", required=False, max_length=50, widget=forms.TextInput(
#         attrs={"class": "form-control", "autocomplete": "off", "placeholder": "Podaj nazwisko"}))
#     email = forms.EmailField(label="Email", required=True, max_length=50, widget=forms.EmailInput(
#         attrs={"class": "form-control", "autocomplete": "off", "placeholder": "Podaj email"}),
#                              error_messages={'invalid': "Nieprawidłowy email"})
#     profile_pic = forms.CharField(label="Profile Pic", max_length=50,
#                                   widget=forms.FileInput(attrs={"class": "form-control"}), required=False)


# class AddAdminForm(forms.Form):
#     first_name = forms.CharField(label="First Name", max_length=50,
#                                  widget=forms.TextInput(attrs={"class": "form-control"}))
#     last_name = forms.CharField(label="Last Name", max_length=50,
#                                 widget=forms.TextInput(attrs={"class": "form-control"}))
#     email = forms.EmailField(label="Email", max_length=50,
#                              widget=forms.EmailInput(attrs={"class": "form-control", "autocomplete": "off"}))


class AddManagerForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=50,
                                 widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
    username = forms.CharField(label="Username", max_length=50,
                               widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}))
    email = forms.EmailField(label="Email", max_length=50,
                             widget=forms.EmailInput(attrs={"class": "form-control", "autocomplete": "off"}))
    password = forms.CharField(label="Password", max_length=50,
                               widget=forms.PasswordInput(attrs={"class": "form-control"}))
    company = forms.CharField(label="Company", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))



