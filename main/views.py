from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from urllib.parse import urlencode
import datetime as dt
from pytz import timezone
import pandas as pd
import json
from .forms import CreateNewPosition
from .models import Position, Order, Trade, EquityPosition, OptionPosition
from utils.TDRestAPI import Rest_Account
from utils.resthandler import RestHandler, DatabaseHandler
import os
import sqlite3
import time
import uuid

#GLOBAL VARIABLES
# VS code keys location
# REST_API = Rest_Account('utils\keys.json')
REST_API = Rest_Account('keys.json')


ORDER_ACTION_CHOICES = {1: "Buy",
                        2: "Sell",
                        3: "Buy to Cover",
                        4: "Sell Short"}
ORDER_TYPE_CHOICES = {1: "Limit",
                    2: "Market",
                    3: "Stop Market",
                    4: "Stop Limit",
                    5: "Trailing Stop %",
                    6: "Traling Stop $"}
ORDER_EXPIRATION_CHOICES = {1: "Day", 2:"GTC"}

# VS code db.
# DATABASE = r'C:\Users\charl\Desktop\BROkerage\papertrade\utils\tda_db.sqlite3'
DATABASE = r'tda_db.sqlite3'
DATABASE_HANDLER = DatabaseHandler()
DATABASE_CONNECTION = DATABASE_HANDLER.create_connection(DATABASE)
REST_HANDLER = RestHandler(REST_API)
# STREAMER_HANDLER = StreamerHandler()


def clear_positions(response):
    user = response.user
    for position in user.positions.all():
        position.delete()
    return render(response, "main/home.html")

def testview(response):
    return render(response, "main/test.html")

async def websocket_view(socket):
    print(socket)
    await socket.accept()
    while True:
        message = await socket.receive_text()
        await socket.send_text(message)

def home(response):
    return render(response, "main/home.html")

def get_position_dict(position):
    if type(position) == dict:
        symbol = position['symbol']
        quantity = position['quantity']
        purchase = position['fill_price']
    else:
        symbol = position.symbol
        quantity = position.quantity
        purchase = position.fill_price
    cur = DATABASE_CONNECTION.cursor()
    columns = ['symbol','mark','quantity','asset','purchase','day_gain_dollar','change','day_gain_perc','gain_dollar','gain_per','delta','theta','gamma','vega']
    return_dict = {}
    for col in columns:
        return_dict[col] = None
    if not symbol in REST_HANDLER.get_symbols():
        REST_HANDLER.add_symbol(symbol)
        time.sleep(2)
    if DATABASE_HANDLER.check_symbol_exist(DATABASE_CONNECTION, symbol):
        sql = "SELECT mark,closePrice,assetType,delta,gamma,theta,vega from tda_data WHERE symbol ='%s'"%(symbol)
        cur.execute(sql)
        data = cur.fetchall()[0]
        mark = round(data[0],2)
        close_price = round(data[1],2)
        asset = data[2]
        delta = data[3]
        gamma = data[4]
        theta = data[5]
        vega = data[6]
        day_gain_dollar = round((mark-close_price)*quantity,2)
        value = round(close_price*quantity, 2)
        day_gain_perc = round((day_gain_dollar/value)*100,2)
        change = round(mark-close_price, 2)
        gain_dollar = round((mark*quantity) - (purchase*quantity),2)
        gain_perc = round(((mark/purchase)-1)*100,2)
    else:
        REST_HANDLER.add_symbol(symbol)
        print('Added ', symbol)
        mark = None
        asset = None
        day_gain_dollar = None
        change = None
        day_gain_perc = None
        gain_dollar = None
        gain_perc = None
        delta = None
        theta = None
        gamma = None
        vega = None
    return_dict['symbol'] = symbol
    return_dict['mark'] = mark
    return_dict['quantity'] = quantity
    return_dict['asset'] = asset
    return_dict['purchase'] = purchase
    return_dict['day_gain_dollar'] = day_gain_dollar
    return_dict['change'] = change
    return_dict['day_gain_perc'] = day_gain_perc
    return_dict['gain_dollar'] = gain_dollar
    return_dict['gain_perc'] = gain_perc
    return_dict['delta'] = delta
    return_dict['theta'] = theta
    return_dict['gamma'] = gamma
    return_dict['vega'] = vega
    return return_dict

def calc_df(df, exclude_zeros=True):
    total_spent = 0
    total_qty = 0
    for index, row in df.iterrows():
        if row['quantity'] > 0:
            total_spent += row['quantity']*row['fill_price']
            total_qty += row['quantity']
    avg_price = total_spent/total_qty
    true_qty = sum(df['quantity'])
    if exclude_zeros:
        if not true_qty == 0:
            df.reset_index(inplace=True)
            return get_position_dict({'symbol':df['symbol'][0], 'quantity':true_qty, 'fill_price':avg_price})

def calc_trade(df):
    if sum(df['quantity']) == 0:
        received = 0
        spent = 0
        for index, row in df.iterrows():
            if row['quantity'] > 0:
                spent += row['quantity']*row['fill_price']
            elif row['quantity'] < 0:
                received += row['quantity']*row['fill_price']*-1
        perc_profit = round(((received-spent)/spent)*100,2)
        dollar_profit = round(received-spent, 2)
        df.reset_index(inplace=True)
        open_date = df['order_execution_date'].iloc[0]
        close_date = df['order_execution_date'].iloc[-1]
        return {'symbol':df['symbol'][0], 'perc_profit':perc_profit, 'dollar_profit':dollar_profit, 'date_opened':open_date, 'date_close':close_date}

def account(response):
    user = response.user
    positions = user.positions.all()
    df = pd.DataFrame(list(positions.values()))
    dfs = []
    ids = set(list(df['position_id']))
    for pid in ids:
        dfs.append(df[df['position_id'] == pid])
    positions = [calc_df(df) for df in dfs if calc_df(df) is not None]
    return render(response, "main/account.html", {'positions': positions})

def history(response, order_trades):
    user = response.user
    positions = user.positions.all()
    if order_trades == 'trades':
        df = pd.DataFrame(list(positions.values()))
        dfs = []
        ids = set(list(df['position_id']))
        for pid in ids:
            dfs.append(df[df['position_id'] == pid])
        positions = [calc_trade(df) for df in dfs if calc_trade(df) is not None]
        return render(response, "main/history.html", {'positions': positions, 'trades': True})
    else:
        return render(response, "main/history.html", {'positions': positions, 'trades': False})

def stats(response):
    user = response.user
    positions = user.positions.all()
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
    return render(response, "main/stats.html", {'wins': wins, 'losses': losses, 'profit':total_profit})

def trade(response):
    if response.method == "POST":
        return redirect("/tradesymbol/" + str(response.POST['searchBar']))
    data = pd.read_csv('utils/stock_symbols.csv')
    symbols = data['Symbol'].to_list()
    company_names = data['Name'].to_list()
    for item in company_names:
        symbols.append(item)
    symbols = json.dumps(symbols)
    return render(response, "main/trade.html", {'autofill_symbols': symbols,})

def tradesymbol(response, symbol):
    user = response.user
    fmt = "%m/%d/%Y, %I:%M:%S"
    eastern = timezone('US/Eastern')
    curr_time = dt.datetime.now(eastern).strftime(fmt)
    if response.method == "POST":
        form = CreateNewPosition()
        print(response.POST)
        form = CreateNewPosition(response.POST)
        if form.is_valid():
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
            cleaned = form.cleaned_data
            cur = DATABASE_CONNECTION.cursor()
            quantity = float(cleaned['quantity'])
            action = cleaned['action']
            # if the action was 2, (sell) flip quantity sign
            if action == "2":
                quantity = quantity*-1
            added = False
            # Check to see if the is in the database, if its not, add it and wait.
            while not DATABASE_HANDLER.check_symbol_exist(DATABASE_CONNECTION, symbol):
                if not added:
                    REST_HANDLER.add_symbol(symbol)
                    print('Added ', symbol)
                time.sleep(1)
            # If we are selling/buying we will go for either the bid or the ask price
            if quantity > 0:
                sql = "SELECT askPrice from tda_data WHERE symbol ='%s'"%(symbol)
            elif quantity < 0:  
                sql = "SELECT bidPrice from tda_data WHERE symbol ='%s'"%(symbol)
            else:
                # If the quantity is 0 just return the page, things are being weird.
                return render(response, "main/tradesymbol.html", {'stock_symbol':symbol, 'curr_time':curr_time, "form":form})
            cur.execute(sql)
            # Get our fill price for this specific order.
            fill_price = round(cur.fetchall()[0][0],2)
            order_type = cleaned['order_type']
            order_expiration = cleaned['order_expiration']
            order_execution_date = dt.datetime.now(eastern)
            # If our limit price is none, ie market price, set it to -999 to avoid db conflicts.
            limit_price = cleaned['limit_price']
            if limit_price is None:
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
            return redirect('/account/')
    else:
        form = CreateNewPosition()
    return render(response, "main/tradesymbol.html", {'stock_symbol':symbol, 'curr_time':curr_time, "form":form})
    

def tradesymbol_chain(response, symbol):
    fmt = "%m/%d/%Y, %I:%M:%S"
    eastern = timezone('US/Eastern')
    curr_time = dt.datetime.now(eastern).strftime(fmt)
    chain = REST_API.get_options_chain(symbol, time_delta=720, strike_count=1, contract_type='CALL')
    expiries = chain['description'].to_list()
    expiries = [' '.join(expiry.split(' ')[:4]) for expiry in expiries]
    expiries = json.dumps(expiries)
    return render(response, "main/tradesymbolchain.html", {'stock_symbol':symbol, 'curr_time':curr_time, "chain":chain, "expiries":expiries})

def get_option_chain(response, symbol, description):
    chain = REST_API.get_options_chain(symbol, time_delta=720, strike_count=12, contract_type='ALL')
    
    chain['description'] = chain['description'].apply(lambda x: ' '.join(x.split(' ')[:4]))
    def parse_strike(strike):
        strike = strike.split('_')[1]
        if 'P' in strike:
            return strike.split('P')[1]
        elif 'C' in strike:
            return strike.split('C')[1]
    chain['strike'] = chain.index.to_series().apply(parse_strike)
    chain = chain[chain['description'] == description]
    indexes = chain.index.to_list() 
    chain = json.dumps(chain.to_json())
    test_dict = json.dumps([{'test':{'one':1,'two':2,'three':3}}])
    indexes = json.dumps(indexes)
    return JsonResponse({'chain':chain, 'indexes':indexes, 'test':test_dict})

def getdata(response, symbol):
    json_response = {}
    cur = DATABASE_CONNECTION.cursor()
    sql = "SELECT bidPrice,askPrice,mark,markPercentChangeInDouble from tda_data WHERE symbol ='%s'"%(symbol)
    cur.execute(sql)
    data = cur.fetchall()[0]
    json_response['bid'] = round(data[0],2)
    json_response['ask'] = round(data[0],2)
    json_response['mark'] = round(data[0],2)
    json_response['mark_percent_change'] = round(data[0],2)
    return JsonResponse(json_response)

def tradesymbolclock(response):
    fmt = "%m/%d/%Y, %I:%M:%S"
    eastern = timezone('US/Eastern')
    curr_time = dt.datetime.now(eastern).strftime(fmt)
    return JsonResponse({"clocktime": curr_time})

def account_positions(response):
    user = response.user
    positions = user.positions.all()

    positions = user.positions.all()
    df = pd.DataFrame(list(positions.values()))
    dfs = []
    ids = set(list(df['position_id']))
    for pid in ids:
        dfs.append(df[df['position_id'] == pid])
        
    return_dict = {}
    columns = ['mark','day_gain_dollar','change','day_gain_perc','gain_dollar','gain_perc','delta','gamma','theta','vega']
    for col in columns:
        return_dict[col] = []
    for df in dfs:
        symbol = df.reset_index()['symbol'][0]
        position_dict = calc_df(df)
        if position_dict is not None:
            for col in columns:
                return_dict[col].append({symbol:position_dict[col]})
    return JsonResponse(return_dict)