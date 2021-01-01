from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("account/", views.account, name='account'),
    path("trade/", views.trade, name='trade'),
    path("tradesymbol/<str:symbol>", views.tradesymbol, name='tradesymbol'),
    path("tradesymbol/clock/", views.tradesymbolclock, name='clockupdate'),
    path("updateaccountdata/", views.account_positions, name='updateaccount')
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