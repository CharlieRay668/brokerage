from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import datetime as dt
# Create your views here.

def dashboard(response):
    return render(response, "externalcode/dashboard.html")

def check_external(response):
    lines = open("status.txt", "r").readlines()
    status_json = {}
    statuses = ["discord_bot_result", "tda_db_result"]
    for line in lines:
        if "tda_db_result:" in line:
            result = line.split(":")[1].strip()
            last_update = dt.datetime.strptime(result, "%m/%d/%Y, %H-%M-%S")
            now = dt.datetime.now()
            difference = now-last_update
            if difference.total_seconds() > 60:
                status_json['tda_db_result'] = "OFFLINE"
            else:
                status_json['tda_db_result'] = "ONLINE"
    status_json['discord_bot_result'] = "ONLINE"
    return JsonResponse(status_json)