from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.shortcuts import render
from django.contrib.auth import login, authenticate

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
            login(response, user)
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
            login(response, user)
        return redirect('/home')
    else:
        form = LoginForm()
    
    return render(response, 'registration/login.html', {"form":form})