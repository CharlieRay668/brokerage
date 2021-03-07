from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="basboarad"),
    path("checkexternalcode/", views.check_external, name="checkstatus")
]