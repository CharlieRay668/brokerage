from django.urls import path
from . import views

urlpatterns = [
    path("", views.prompt_view, name="promptview"),
    path("create/", views.create, name="create"),
    path("view/<int:act_id>/", views.view, name="accountview")
]