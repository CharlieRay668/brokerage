from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from main.models import Position
from django.forms.models import model_to_dict
from pytz import timezone
import datetime as dt

api_keys = ["charliekey", "billkey"]
eastern = timezone('US/Eastern')

def documentation(response):
    return render(response, "api/documentation.html")

@csrf_exempt
def get_activity(response):
    api_key = response.headers['apikey']
    if api_key not in api_keys:
        return HttpResponse("Permission Denied", status=403)
    return_dict = {}
    fields = ['user', 'position_id', 'symbol', 'quantity', 'fill_price', 'position_info', 'order_action', 'order_type', 'order_expiration', 'order_execution_date', 'limit_price']
    from_date = False
    to_date = False
    if response.method == "POST":
        fields = response.POST.get('fields', fields)    
        from_date = response.POST.get('from_date', False)
        to_date = response.POST.get('to_date', False)
    
    if not from_date and not to_date:
        positions = Position.objects.all()
    elif not to_date:
        from_date = dt.datetime.fromisoformat(from_date)
        positions = Position.objects.filter(order_execution_date__range=(from_date,dt.datetime.now(eastern)))
    else:
        from_date = dt.datetime.fromisoformat(from_date)
        to_date = dt.datetime.fromisoformat(to_date)
        positions = Position.objects.filter(order_execution_date__range=(from_date,to_date))
    for position in positions:
        print(position.fill_price)
        return_dict[position.id] = model_to_dict(position, fields=fields)
        if 'user' in fields:
            return_dict[position.id]['user'] = position.user.email
    return JsonResponse(return_dict)

def test(response):
    return_dict = {}
    return_dict['Hello'] = "World"
    return JsonResponse(return_dict)

@csrf_exempt
def posttest(response):
    return_dict = {}
    post_data = response.POST
    api_key = response.headers['apikey']
    if api_key not in api_keys:
        return HttpResponse("Permission Denied", status=403)
    return_dict['Hello'] = post_data['repeat']
    return JsonResponse(return_dict)