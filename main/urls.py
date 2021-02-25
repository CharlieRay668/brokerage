from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("account/", views.account, name='account'),
    path("trade/", views.trade, name='trade'),
    path("tradesymbol/<str:symbol>/", views.tradesymbol, name='tradesymbol'),
    path("tradesymbol/<str:symbol>/<str:buy_sell>", views.tradesymbol, name='tradesymbolbs'),
    path("tradesymbol/<str:symbol>/option/", views.tradesymbol_chain, name='tradesymbolchain'),
    path("getdata/<str:symbol>", views.getdata, name='getdata'),
    path("getchain/<str:symbol>/<str:description>/<int:strike_count>", views.get_option_chain, name='getchain'),
    #path("optionorder/<str:expiry>/<float:strike>/<str:side>/<str:buy_sell>", views.optionorder, name='optionorder'),
    path("tradesymbol/clock/", views.tradesymbolclock, name='clockupdate'),
    path("updateaccountdata/", views.account_positions, name='updateaccount'),
    path("test/", views.testview, name='testview'),
    path("deleteall/", views.clear_positions, name='deleteall'),
    path("history/<str:order_trades>", views.history, name='history'),
    path("stats/", views.stats, name='stats'),
    path("test/", views.testview, name='test'),
    path("testping/", views.get_symbols_from_rh, name='testping'),
    path("profile/", views.profile, name='profile'),
]