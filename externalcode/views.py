from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

# Create your views here.

def dashboard(response):
    return render(response, "externalcode/dashboard.html")