from django.urls import path
from . import views

urlpatterns = [
    path("activity/", views.get_activity, name="activity"),
    path("create/", views.create_position, name="create"),
    path("userpositions/", views.get_user_positions, name="userpositions"),
    path("stats/", views.get_user_stats, name="userstats"),
    path("history/", views.get_user_history, name="userhistory"),
    path("ranking/", views.get_rankings, name="rankings"),
    path("users/", views.get_users, name='users'),
    path("useraccount/", views.get_user_account, name='useraccount'),
    path("account/", views.get_balance, name="account"),
    path("docs/", views.documentation, name='documentation')
]