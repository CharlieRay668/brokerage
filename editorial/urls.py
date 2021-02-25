from django.urls import path
from . import views

urlpatterns = [
    path("edit/", views.edit, name="edit"),
    path("edit/updatepos/", views.updatepos, name="updatepos")
]