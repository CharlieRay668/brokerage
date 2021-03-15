from django.urls import path
from . import views

urlpatterns = [
    path("", views.trade, name='trade'),
    path("<str:symbol>/", views.tradesymbol, name='tradesymbol'),
    path("<str:symbol>/option/", views.tradesymbol_chain, name='tradesymbolchain'),
    path("<str:symbol>/<str:buy_sell>/", views.tradesymbol, name='tradesymbolbs'),
]