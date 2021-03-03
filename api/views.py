from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from main.models import Position
from main.views import calc_df, calc_trade
from users.models import User
from utils.resthandler import RestHandler, DatabaseHandler
from django.forms.models import model_to_dict
from pytz import timezone
import datetime as dt
import time
import uuid
import pandas as pd

api_keys = ["charliekey", "billkey"]
eastern = timezone('US/Eastern')
DATABASE = r'tda_db.sqlite3'
DATABASE_HANDLER = DatabaseHandler()
DATABASE_CONNECTION = DATABASE_HANDLER.create_connection(DATABASE)
REST_HANDLER = RestHandler()

def documentation(response):
    return render(response, "api/documentation.html")

# @csrf_exempt
# def get_price_data(response):
#     api_key = response.headers['apikey']
#     if api_key not in api_keys:
#         return HttpResponse("Permission Denied", status=403)
#     if response.method == "POST":
#         symbol = response.POST['symbol']
#         fields = response.POST['fields']
#         if not symbol in REST_HANDLER.get_symbols():
#             REST_HANDLER.add_symbol(symbol)
#             time.sleep(2)
#         cur = DATABASE_CONNECTION.cursor()
#
#          sql = "SELECT * from tda_data WHERE symbol ='%s'"%(symbol)
@csrf_exempt
def get_rankings(response):
    api_key = response.headers['apikey']
    if api_key not in api_keys:
        return HttpResponse("Permission Denied", status=403)
    if response.method == "POST":
        number = response.POST.get('number', False)
        from_date = response.POST.get('from_date', False)
        to_date = response.POST.get('to_date', False)
        if not from_date or not to_date:
            return HttpResponse("Date range not given", 304)
        from_date = dt.datetime.fromisoformat(from_date)
        to_date = dt.datetime.fromisoformat(to_date)
        users = User.objects.all()
        rankings = []
        for user in users:
            positions = user.positions.all()
            positions = positions.filter(order_execution_date__range=(from_date,to_date))
            if len(positions) != 0:
                df = pd.DataFrame(list(positions.values()))
                dfs = []
                ids = set(list(df['position_id']))
                for pid in ids:
                    dfs.append(df[df['position_id'] == pid])
                positions = [calc_trade(df) for df in dfs if calc_trade(df) is not None]
                wins = 0
                losses = 0
                total_profit = 0
                for position in positions:
                    if from_date <= position['date_closed'] <= to_date:
                        profit = position['perc_profit']
                        if profit > 0:
                            wins += 1
                        else:
                            losses += 1
                        total_profit += profit
                        rankings.append({'username': user.username, 'profit': total_profit, 'wins': wins, 'losses':losses})
        if not number:
            rankings = sorted(rankings, key = lambda i: i['profit'],reverse=True)
        else:
            rankings = sorted(rankings, key = lambda i: i['profit'],reverse=True)[:number]
        return JsonResponse({'rankings':rankings})
    return HttpResponse("Attempted to GET a POST endpoint", status=303)

@csrf_exempt
def get_user_history(response):
    api_key = response.headers['apikey']
    if api_key not in api_keys:
        return HttpResponse("Permission Denied", status=403)
    if response.method == "POST":
        username = response.POST.get('username', False)
        try:
            user = User.objects.get(username=username)
        except:
            return HttpResponse("Unkown username", status=305)
        positions = user.positions.all()
        df = pd.DataFrame(list(positions.values()))
        dfs = []
        ids = set(list(df['position_id']))
        for pid in ids:
            dfs.append(df[df['position_id'] == pid])
        positions = [calc_trade(df) for df in dfs if calc_trade(df) is not None]
        return JsonResponse({"positions": positions})
    return HttpResponse("Attempted to GET a POST endpoint", status=303)

@csrf_exempt
def get_user_stats(response):
    api_key = response.headers['apikey']
    if api_key not in api_keys:
        return HttpResponse("Permission Denied", status=403)
    if response.method == "POST":
        username = response.POST.get('username', False)
        try:
            user = User.objects.get(username=username)
        except:
            return HttpResponse("Unkown username", status=305)
        positions = user.positions.all()
        if len(positions) == 0:
            return JsonResponse({'profit':0, 'wins':0, 'losses':0})
        df = pd.DataFrame(list(positions.values()))
        dfs = []
        ids = set(list(df['position_id']))
        for pid in ids:
            dfs.append(df[df['position_id'] == pid])
        positions = [calc_trade(df) for df in dfs if calc_trade(df) is not None]
        wins = 0
        losses = 0
        total_profit = 0
        for position in positions:
            profit = position['perc_profit']
            if profit > 0:
                wins += 1
            else:
                losses += 1
            total_profit += profit
        return JsonResponse({'profit':total_profit, 'wins':wins, 'losses':losses})
    return HttpResponse("Attempted to GET a POST endpoint", status=303)

@csrf_exempt
def get_user_positions(response):
    api_key = response.headers['apikey']
    if api_key not in api_keys:
        return HttpResponse("Permission Denied", status=403)
    if response.method == "POST":
        username = response.POST.get('username', False)
        try:
            user = User.objects.get(username=username)
        except:
            return HttpResponse("Unkown username", status=305)
        positions = Position.objects.filter(user=user)
        df = pd.DataFrame(list(positions.values()))
        dfs = []
        ids = set(list(df['position_id']))
        for pid in ids:
            dfs.append(df[df['position_id'] == pid])
        symbols = [position.symbol for position in positions if position.symbol not in REST_HANDLER.get_symbols()]
        updates = []
        for symbol in symbols:
            REST_HANDLER.add_symbol(symbol)
            updates.append(symbol)
        positions = [calc_df(df) for df in dfs if calc_df(df) is not None]
        return JsonResponse({"positions": positions})
    return HttpResponse("Attempted to GET a POST endpoint", status=303)
    

@csrf_exempt
def create_position(response):
    print(response)
    print(response.method)
    print(response.headers)
    api_key = response.headers['apikey']
    if api_key not in api_keys:
        return HttpResponse("Permission Denied", status=403)
    return HttpResponse("response method " + str(response.method) + " headers " + str(response.headers), status=200)
    if response.method == "POST":
        return HttpResponse("Successfully posted", status=200)
        username = response.POST.get('username', False)
        symbol = response.POST.get('symbol', False)
        quantity = response.POST.get('quantity', False)
        action = response.POST.get('action', False)
        order_type = response.POST.get('order_type', False)
        order_expiration = response.POST.get('order_expiration', False)
        limit_price = response.POST.get('limit_price', False)
        info = [username, symbol, quantity, action, order_type, order_expiration]
        if False in info:
            return False
        quantity = int(quantity)
        action = int(action)
        order_type = int(order_type)
        order_expiration = int(order_expiration)
        try:
            user = User.objects.get(username=username)
        except:
            return HttpResponse("Unkown username", status=305)
        order_execution_date = dt.datetime.now(eastern)
        added = False
        while not DATABASE_HANDLER.check_symbol_exist(DATABASE_CONNECTION, symbol):
            if not added:
                REST_HANDLER.add_symbol(symbol)
                added = True
            time.sleep(1)
        # if not symbol in REST_HANDLER.get_symbols():
        #     REST_HANDLER.add_symbol(symbol)
        #     time.sleep(2)
        # Get user positions
        positions = user.positions.all()
        # Generate ID
        position_id = str(uuid.uuid1().hex)
        # Get all positions with same symbol
        matching_positions = [position for position in positions if position.symbol == symbol]
        ids = []
        # Get a set of all the IDs for this symbol
        for position in matching_positions:
            ids.append(position.position_id)
        ids = set(ids)
        # For each ID in the set of IDs, go through and group the positions into groups of the same ID
        groups = []
        for index, pos_id in enumerate(ids):
            groups.append([])
            for position in matching_positions:
                print(position.position_id, pos_id)
                if position.position_id == pos_id:
                    groups[index].append(position)
        # For each group, get the quantity held, if it is not 0 (The user is currently holding some of this stuff) set this new trade ID to be the group
        for position_group in groups:
            group_quantity = 0
            for position in position_group:
                group_quantity += position.quantity
            if group_quantity != 0:
                position_id = position_group[0].position_id
        # Handle order info
        cur = DATABASE_CONNECTION.cursor()
        # if the action was 2, (sell) flip quantity sign
        if action == 2:
            quantity = quantity*-1
        # If we are selling/buying we will go for either the bid or the ask price
        if quantity > 0:
            sql = "SELECT askPrice from tda_data WHERE symbol ='%s'"%(symbol)
        elif quantity < 0:  
            sql = "SELECT bidPrice from tda_data WHERE symbol ='%s'"%(symbol)
        else:
            # If the quantity is 0 return quantity 0 error
            return False
        cur.execute(sql)
        # Get our fill price for this specific order.
        fill_price = round(cur.fetchall()[0][0],2)
        # If our limit price is none, ie market price, set it to -999 to avoid db conflicts.
        if limit_price is False:
            limit_price = -999
        sql = "SELECT * from tda_data WHERE symbol ='%s'"%(symbol)
        cur.execute(sql)
        # Zip the db row into a dictionary to save in a different db, this just takes a snapshot of the market at order execution
        description = cur.description
        columns = [col[0] for col in description]
        position_info = [dict(zip(columns, row)) for row in cur.fetchall()]
        # Create ans save the new position.
        new_position = Position(position_id=position_id, symbol=symbol, quantity=quantity, fill_price=fill_price, position_info=position_info, order_action=action, order_type=order_type, order_expiration=order_expiration, order_execution_date=order_execution_date, limit_price=limit_price)
        new_position.save()
        user.positions.add(new_position)
        return HttpResponse("Success", status=200)
    return HttpResponse("Attempted to GET a POST endpoint", status=303)

@csrf_exempt
def get_activity(response):
    api_key = response.headers['apikey']
    if api_key not in api_keys:
        return HttpResponse("Permission Denied", status=403)
    return_dict = {}
    fields = ['user', 'position_id', 'symbol', 'quantity', 'fill_price', 'position_info', 'order_action', 'order_type', 'order_expiration', 'order_execution_date', 'limit_price']
    from_date = False
    to_date = False
    username = False
    if response.method == "POST":
        fields = response.POST.get('fields', fields)    
        from_date = response.POST.get('from_date', False)
        to_date = response.POST.get('to_date', False)
        username = response.POST.get('username', False)
    if not from_date and not to_date:
        positions = Position.objects.all()
    elif not to_date:
        from_date = dt.datetime.fromisoformat(from_date)
        positions = Position.objects.filter(order_execution_date__range=(from_date,dt.datetime.now(eastern)))
    else:
        from_date = dt.datetime.fromisoformat(from_date)
        to_date = dt.datetime.fromisoformat(to_date)
        positions = Position.objects.filter(order_execution_date__range=(from_date,to_date))
    if username is not False:
        positions = positions.filter(user__username=username)
    for position in positions:
        return_dict[position.id] = model_to_dict(position, fields=fields)
        if 'user' in fields:
            return_dict[position.id]['user'] = position.user.username
        if 'fill_price' in fields:
            return_dict[position.id]['fill_price'] = position.fill_price
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