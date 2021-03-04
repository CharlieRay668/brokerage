from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm, PasswordChangeForm, PasswordRequest
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

User = get_user_model()

def home_view(response):
    return render(response, 'main/home.html')

def prompt_pass_change(response):
    if response.method == "POST":
        form = PasswordRequest(response.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            try:
                user = User.objects.get(email=email)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            if user is not None:
                mail_subject = 'Reset Password'
                current_site = get_current_site(response)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = account_activation_token.make_token(user)
                activation_link = "{0}/passreset/{1}/{2}".format(current_site, uid, token)
                message = "Hello {0},\n Recently someone requested to change your password for Rillion Brokerage. If that was not you ignore this email. Click the link below to change you password.\n {1}".format(user.username, activation_link)
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
                return render(response, 'register/passrequest.html', {"form":form, "success_msg":"A email should have been sent to " + to_email + ", please click the link enclosed to reset your password."})
            return render(response, 'register/passrequest.html', {"form":form, "error_msg":"Unable to find user with specified email"})
        return render(response, 'register/passrequest.html', {"form":form, "error_msg":"Invalid form"})
    else:
        form = PasswordRequest()
        return render(response, "register/passrequest.html", {"form":form})

def change_passowrd(response, uid, token):
    if response.method == "GET":
        try:
            uid = force_text(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            login(response, user)
            form = PasswordChangeForm(response.user)
            return render(response, 'register/passreset.html', {'form': form})
        else:
            return HttpResponse('Password reset link is invalid!')
            
    elif response.method == "POST":
        form = PasswordChangeForm(response.user, response.POST)
        if form.is_valid():
            password = form.cleaned_data.get("password1")
            user.password = password
            user.save()
            update_session_auth_hash(response, user) # Important, to update the session with the new password
            return redirect('/home')

def activate(response, uid, token):
    if response.method == "GET":
        try:
            uid = force_text(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            # activate user and login:
            user.is_active = True
            user.save()
            login(response, user)
            return redirect('/home')
        else:
            return HttpResponse('Activation link is invalid!')

def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # form.save()
            # email = form.cleaned_data.get('email')
            # password = form.cleaned_data.get('password1')
            # user = authenticate(username=email, password=password)
            mail_subject = 'Activate your account.'
            current_site = get_current_site(response)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = "{0}/activate/{1}/{2}".format(current_site, uid, token)
            message = "Hello {0},\n {1}".format(user.username, activation_link)
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            # if user is not None:
            #     login(response, user)
            # else:
            #     form = RegisterForm()
            #     error_msg = "Failed to create account. Your password may be too simple or there may already be a user with this email."
            #     return render(response, 'register/register.html', {"form":form, "error_msg":error_msg})
            return render(response, 'register/register.html', {"form":form, "success_msg":"A email should have been sent to " + to_email + ", please click the link enclosed to activate your account."})
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
    return render(response, 'registration/login.html', {"form":form})