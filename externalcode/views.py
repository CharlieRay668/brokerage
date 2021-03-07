from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

# Create your views here.

def dashboard(response):
    return render(response, "externalcode/dashboard.html")

def check_external(response):
    lines = open("status.txt", "r").readlines()
    status_json = {}
    for line in lines:
        status_json[line.split(":")[0]] = line.split(":")[1]
    return JsonResponse(status_json)