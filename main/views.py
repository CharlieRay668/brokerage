from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from urllib.parse import urlencode
import datetime as dt
#from datetime import timezone
from pytz import timezone
import pandas as pd
import json
from .forms import CreateNewEquityPosition
from .models import Trade, EquityPosition, OptionPosition
from utils.TDRestAPI import Rest_Account
from utils.test import DatabaseHandler, StreamerHandler
import os
import sqlite3
import time

#GLOBAL VARIABLES
REST_API = Rest_Account('utils\keys.json')

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

DATABASE = r'C:\Users\charl\Desktop\BROkerage\papertrade\db.sqlite3'
DATABASE_HANDLER = DatabaseHandler()
DATABASE_CONNECTION = DATABASE_HANDLER.create_connection(DATABASE)
STREAMER_HANDLER = StreamerHandler()

def home(response):
    return render(response, "main/truehome.html")

def get_position_dict(positions):
    return_dict = []
    for position in positions:
        position_dict = {}
        position_dict['symbol'] = position.symbol
        position_dict['quantity'] = position.quantity
        position_dict['day_gain_D'] = 'None'
        position_dict['day_gain_P'] = 'None'
        position_dict['mark'] = 'None'
        position_dict['change_D'] = 'None'
        position_dict['gain_D'] = 'None'
        position_dict['gain_P'] = 'None'
        position_dict['asset'] = 'Equity'
        position_dict['purchase'] = position.fill_price
        position_dict['delta'] = 'None'
        position_dict['theta'] = 'None'
        position_dict['gamma'] = 'None'
        position_dict['vega'] = 'None'
        return_dict.append(position_dict)
    return return_dict

def account(response):
    user = response.user
    return_equity_positions = []
    return_option_positions = []
    for trade in user.trades.all():
        return_equity_positions += get_position_dict(trade.equity_positions.all())
        return_option_positions += get_position_dict(trade.option_positions.all())
    return render(response, "main/account.html", {'equity_positions': return_equity_positions, 'option_positions': return_option_positions})

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
    fmt = "%m/%d/%Y, %I:%M:%S"
    eastern = timezone('US/Eastern')
    curr_time = dt.datetime.now(eastern).strftime(fmt)
    if response.method == "POST":
        form = CreateNewEquityPosition()
        print(response.POST)
        form = CreateNewEquityPosition(response.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            if type(cleaned['limit_price']) is None:
                cleaned['limit_price'] = None
            new_trade = Trade()
            new_trade.save()
            equity_position = EquityPosition(parent_trade=new_trade, symbol=symbol, quantity=cleaned['quantity'], action=cleaned['action'], order_type=cleaned['order_type'], order_expiration=cleaned['order_expiration'], order_execution_date=dt.datetime.now(), fill_price=cleaned['limit_price'], limit_price=cleaned['limit_price'])
            equity_position.save()
            new_trade.equity_positions.add(equity_position)
            response.user.trades.add(new_trade)
    else:
        form = CreateNewEquityPosition()
    return render(response, "main/tradesymbol.html", {'stock_symbol':symbol, 'curr_time':curr_time, "form":form})

def tradesymbolclock(response):
    fmt = "%m/%d/%Y, %I:%M:%S"
    eastern = timezone('US/Eastern')
    curr_time = dt.datetime.now(eastern).strftime(fmt)
    return JsonResponse({"clocktime": curr_time})

def account_positions(response):
    user = response.user
    equitys = []
    options = []
    for trade in user.trades.all():
        equitys += get_position_dict(trade.equity_positions.all())
        options += get_position_dict(trade.option_positions.all())
    symbols = []
    for equity in equitys:
        symbols.append(equity['symbol'])
    cur = DATABASE_CONNECTION.cursor()
    return_dict = {}
    return_dict['mark'] = []
    return_dict['day_gain_dollar'] = []
    return_dict['change'] = []
    return_dict['day_gain_perc'] = []
    for symbol in symbols:
        if not symbol in STREAMER_HANDLER.get_symbols():
            STREAMER_HANDLER.add_symbol(symbol)
            time.sleep(2)
    for equity in equitys:
        symbol = equity['symbol']
        if DATABASE_HANDLER.check_symbol_exist_equity(DATABASE_CONNECTION, symbol):
            sql = "SELECT mark from utils_data_logs_equity WHERE symbol ='%s'"%(symbol)
            cur.execute(sql)
            mark = round(cur.fetchall()[0][0],2)
            sql = "SELECT close_price FROM utils_data_logs_equity WHERE symbol = '%s'"%(symbol)
            cur.execute(sql)
            close_price = cur.fetchall()[0][0]
            day_gain_dollar = round((mark-close_price)*equity['quantity'],2)
            value = round(close_price*equity['quantity'], 2)
            day_gain_perc = round((day_gain_dollar/value)*100,2)
            change = round(mark-close_price, 2)
        else:
            STREAMER_HANDLER.add_symbol(symbol)
            print('Added ', symbol)
            mark = None
            close_price = None
            day_gain_dollar = None
            change = None
        return_dict['mark'].append({symbol:mark})
        return_dict['day_gain_dollar'].append({symbol:day_gain_dollar})
        return_dict['change'].append({symbol:change})
        return_dict['day_gain_perc'].append({symbol:day_gain_perc})
    return JsonResponse(return_dict)