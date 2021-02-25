from django.urls import path
from . import views

urlpatterns = [
    path("activity/", views.get_activity, name="activity"),
    path("create/", views.create_position, name="create"),
    path("userpositions/", views.get_user_positions, name="userpositions"),
    path("test/", views.test, name = "test"),
    path("posttest/", views.posttest, name = "posttest"),
    path("docs/", views.documentation, name='documentation')
]