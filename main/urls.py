from django.urls import path
from . import views
from custom_websocket.urls import websocket

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("account/", views.account, name='account'),
    path("trade/", views.trade, name='trade'),
    path("tradesymbol/<str:symbol>/", views.tradesymbol, name='tradesymbol'),
    path("tradesymbol/<str:symbol>/option/", views.tradesymbol_chain, name='tradesymbolchain'),
    path("getdata/<str:symbol>", views.getdata, name='getdata'),
    path("getchain/<str:symbol>/<str:description>", views.get_option_chain, name='getchain'),
    #path("optionorder/<str:expiry>/<float:strike>/<str:side>/<str:buy_sell>", views.optionorder, name='optionorder'),
    path("tradesymbol/clock/", views.tradesymbolclock, name='clockupdate'),
    path("updateaccountdata/", views.account_positions, name='updateaccount'),
    path("test/", views.testview, name='testview'),
    path("deleteall/", views.clear_positions, name='deleteall'),
    path("history/<str:order_trades>", views.history, name='history'),
    path("stats/", views.stats, name='stats'),
    path("activity/", views.get_activity, name='activity'),
    websocket("ws/", views.websocket_view)
    # path("create/", views.create, name="create"),
    # path("viewclass/<str:classname>/", views.viewclass, name="ap"),
    # path("answer/<int:id>/", views.answerquestion, name="answerquestion"),
    # path("addquestion/<int:id>/", views.updatesame, name="updatesame"),
    # path("removequestion/<int:id>/", views.removesame, name="removesame"),
    # path("view/", views.viewpersonalized, name='view'),
    # path("classcreate/", views.classcreate, name="classcreate"),
    # path("handlesort", views.handlesearch, name ='handlesort'),
    # path("viewclass/<str:classname>/<str:sort>/<int:num_days>/", views.viewsortedclass, name='viewclass'),
    # path('viewsearch', views.viewsearch, name='viewsearch')
]