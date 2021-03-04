from django_registration.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from users.models import User
from django import forms

class PasswordRequest(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'email'}))

class PasswordChangeForm(RegistrationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ["password1", "password2"]

class RegisterForm(RegistrationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2"]

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '',
            'id': 'password',
        }))

