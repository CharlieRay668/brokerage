from django.urls import path
from . import views

urlpatterns = [
    path("testassign/", views.assignview, name="assignment"),
]