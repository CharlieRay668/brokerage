from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail



def home_view(response):
    return render(response, 'main/home.html')

def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(response, user)
            else:
                form = RegisterForm()
                error_msg = "Failed to create account. Your password may be too simple or there may already be a user with this email."
                return render(response, 'register/register.html', {"form":form, "error_msg":error_msg})
            return redirect("/home")
    else:
        form = RegisterForm()
    return render(response, "register/register.html", {"form":form})

def signin(response):
    if response.method == "POST":
        form = LoginForm(response.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(response, user)
            else:
                form = LoginForm()
                error_msg = "Failed to sign in, wrong password or email"
                return render(response, 'registration/login.html', {"form":form, "error_msg":error_msg})
            return redirect('/home')
    else:
        form = LoginForm()
        send_mail(
            'Test Subject',
            'This is a test email!',
            'support@rillionbrokerage.com',
            ['charlie.ray84@gmail.com'],
            fail_silently=False,
        )
    
    return render(response, 'registration/login.html', {"form":form})