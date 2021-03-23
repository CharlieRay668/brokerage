from django.urls import path
from . import views

urlpatterns = [
    path("activity/", views.get_activity, name="activity"),
    path("create/", views.create_position, name="create"),
    path("userpositions/", views.get_user_positions, name="userpositions"),
    path("stats/", views.get_user_stats, name="userstats"),
    path("history/", views.get_user_history, name="userhistory"),
    path("ranking/", views.get_rankings, name="rankings"),
    path("docs/", views.documentation, name='documentation')
]