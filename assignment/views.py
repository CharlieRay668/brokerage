from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from assigner import assign
# Create your views here.


def assignview(response):
    return HttpResponse(str(assign()))
