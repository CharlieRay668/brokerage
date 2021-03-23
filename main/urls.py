from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("getdata/<str:symbol>", views.getdata, name='getdata'),
    path("getchain/<str:symbol>/<str:description>/<int:strike_count>", views.get_option_chain, name='getchain'),
    path("tradesymbol/clock/", views.tradesymbolclock, name='clockupdate'),
    path("updateaccountdata/<int:act_id>/", views.account_positions, name='updateaccount'),
    path("deleteall/", views.clear_positions, name='deleteall'),
    path("history/<str:order_trades>", views.history, name='history'),
    path("stats/", views.stats, name='stats'),
    path("profile/", views.profile, name='profile'),
    path("charts/", views.charts, name="charts"),
]