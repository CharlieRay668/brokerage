from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from urllib.parse import urlencode
import datetime as dt
from pytz import timezone
import pandas as pd
import json
from .forms import CreateNewBuyPosition, CreateNewSellPosition
from .models import Position
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

def home(response):
    return render(response, "main/home.html")

def charts(response):
    history = REST_API.history('TSLA', frequency=1, days=100, frequency_type='daily', period_type='month')
    data = []
    for index, row in history.iterrows():
        data.append([str(index), row['open'], row['high'], row['low'], row['close']])
    return render(response, "main/charts.html", {'stock_data':data})

# REST CHANGE
def get_position_dict(position):
    if type(position) == dict:
        symbol = position['symbol']
        quantity = position['quantity']
        purchase = round(position['fill_price'],2)
    else:
        symbol = position.symbol
        quantity = position.quantity
        purchase = round(position.fill_price,2)
    cur = DATABASE_CONNECTION.cursor()
    columns = ['symbol','mark','quantity','asset','purchase','day_gain_dollar','change','day_gain_perc','gain_dollar','gain_per','delta','theta','gamma','vega']
    return_dict = {}
    for col in columns:
        return_dict[col] = None
    # added = False
    # while not DATABASE_HANDLER.check_symbol_exist(DATABASE_CONNECTION, symbol):
    #     if not added:
    #         REST_HANDLER.add_symbol(symbol)
    #         added = True
    #     time.sleep(1)
    if not symbol in REST_HANDLER.get_symbols():
        REST_HANDLER.add_symbol(symbol)
    if DATABASE_HANDLER.check_symbol_exist(DATABASE_CONNECTION, symbol):
        sql = "SELECT mark,closePrice,assetType,delta,gamma,theta,vega,description from tda_data WHERE symbol ='%s'"%(symbol)
        cur.execute(sql)
        data = cur.fetchall()[0]
        mark = round(data[0],2)
        close_price = round(data[1],2)
        asset = data[2]
        delta = data[3]
        gamma = data[4]
        theta = data[5]
        vega = data[6]
        description = data[7]
        if asset == 'OPTION':
            day_gain_dollar = round(((mark-close_price)*quantity)*100,2)
            gain_dollar = round(((mark*quantity) - (purchase*quantity))*100,2)
            value = round(close_price*quantity*100, 2)
        else:
            gain_dollar = round((mark*quantity) - (purchase*quantity),2)
            day_gain_dollar = round((mark-close_price)*quantity,2)
            value = round(close_price*quantity, 2)
        if value == 0:
            day_gain_perc = 0
        else:
            day_gain_perc = round((day_gain_dollar/value)*100,2)
        if purchase == 0:
            gain_perc = 0
        else:
            gain_perc = round(((mark/purchase)-1)*100,2)
        change = round(mark-close_price, 2)
        if quantity < 0:
            gain_perc *= -1
            day_gain_perc *= -1
    else:
        REST_HANDLER.add_symbol(symbol)
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
        description = None

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
    return_dict['description'] = description
    return return_dict

def calc_df(df, exclude_zeros=True):
    total_spent = 0
    total_qty = 0
    for index, row in df.iterrows():
        if row['quantity'] != 0:
            total_spent += row['quantity']*row['fill_price']
            total_qty += row['quantity']
    if total_qty != 0:
        avg_price = total_spent/total_qty
        true_qty = sum(df['quantity'])
        if exclude_zeros:
            if not true_qty == 0:
                df.reset_index(inplace=True)
                return get_position_dict({'symbol':df['symbol'][0], 'quantity':true_qty, 'fill_price':avg_price})

def calc_trade(df):
    if sum(df['quantity']) == 0:
        asset_type = df['position_info'].iloc[0][0]['assetType']
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
        if asset_type == 'OPTION':
            dollar_profit = dollar_profit*100
        return {'symbol':df['symbol'][0], 'perc_profit':perc_profit, 'dollar_profit':dollar_profit, 'date_opened':open_date, 'date_close':close_date}

def history(response, order_trades):
    user = response.user
    positions = user.positions.all()
    if order_trades == 'trades':
        if len(positions) == 0:
            return render(response, "main/history.html", {'positions': positions, 'trades': True})
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
    if len(positions) == 0:
        return render(response, "main/stats.html", {'wins': 0, 'losses': 0, 'profit':0})
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
    user = response.user
    accounts = user.accounts.all()
    if len(accounts) == 0:
        return redirect("/accounts/create/")
    if len(accounts) == 1:
        account = accounts[0]
        return redirect("/trade/"+str(account.id)+"/")
    return render(response, "main/prompt_trade.html", {"accounts": accounts})

def get_specific_date(description):
    lookup = {'Jan' : '01','Feb' : '02','Mar' : '03','Apr' : '04','May' : '05','Jun' : '06','Jul' : '07','Aug' : '08','Sep' : '09','Oct' : '10','Nov' : '11','Dec' : '12'}
    description = description.split(' ')
    month = lookup[description[1]]
    day = description[2]    
    year = description[3]
    if len(day) < 2:
        day = '0'+day
    return year +'-'+ month +'-'+ day

def profile(response):
    if response.method == "POST":
        username = response.POST['username']
        response.user.username = username
        response.user.save()
    return render(response, "main/profile.html")

# JSON Responses

def get_option_chain(response, symbol, description, strike_count):
    specific_date = get_specific_date(description)
    chain = REST_API.get_options_chain(symbol, time_delta=720, strike_count=strike_count, contract_type='ALL', specific_date=specific_date)
    chain['description'] = chain['description'].apply(lambda x: ' '.join(x.split(' ')[:4]))
    def parse_strike(strike):
        strike = strike.split('_')[1]
        if 'P' in strike:
            return strike.split('P')[1]
        elif 'C' in strike:
            return strike.split('C')[1]
    chain['strike'] = chain.index.to_series().apply(parse_strike)
    indexes = chain.index.to_list() 
    chain = json.dumps(chain.to_json())
    indexes = json.dumps(indexes)
    return JsonResponse({'chain':chain, 'indexes':indexes})

# REST CHANGER
def getdata(response, symbol):
    json_response = {}
    cur = DATABASE_CONNECTION.cursor()
    added = False
    x = 0
    if symbol not in REST_HANDLER.get_symbols():
        REST_HANDLER.add_symbol(symbol)
    if not DATABASE_HANDLER.check_symbol_exist(DATABASE_CONNECTION, symbol):
        json_response['bid'] = 0
        json_response['ask'] = 0
        json_response['mark'] = 0
        json_response['mark_percent_change'] = 0
        json_response['symbols'] = REST_HANDLER.get_symbols()
        return JsonResponse(json_response)
    sql = "SELECT bidPrice,askPrice,mark,markPercentChangeInDouble from tda_data WHERE symbol ='%s'"%(symbol)
    cur.execute(sql)
    data = cur.fetchall()[0]
    json_response['bid'] = round(data[0],2)
    json_response['ask'] = round(data[1],2)
    json_response['mark'] = round(data[2],2)
    json_response['mark_percent_change'] = round(data[3],2)
    json_response['symbols'] = REST_HANDLER.get_symbols()
    return JsonResponse(json_response)

def tradesymbolclock(response):
    fmt = "%m/%d/%Y, %I:%M:%S"
    eastern = timezone('US/Eastern')
    curr_time = dt.datetime.now(eastern).strftime(fmt)
    return JsonResponse({"clocktime": curr_time})

def account_positions(response, act_id):
    account = response.user.accounts.get(id=act_id)
    positions = account.acct_positions.all()
    df = pd.DataFrame(list(positions.values()))
    dfs = []
    ids = set(list(df['position_id']))
    for pid in ids:
        dfs.append(df[df['position_id'] == pid])
        
    return_dict = {}
    columns = ['mark','day_gain_dollar','change','day_gain_perc','gain_dollar','gain_perc','delta','gamma','theta','vega']
    for col in columns:
        return_dict[col] = []
    option_value = 0
    equity_value = 0
    symbols = []
    for df in dfs:
        symbols.append(df.reset_index()['symbol'][0])
    for symbol in symbols:
        if symbol not in REST_HANDLER.get_symbols():
            REST_HANDLER.add_symbol(symbol)
    for df in dfs:
        symbol = df.reset_index()['symbol'][0]
        position_dict = calc_df(df)
        if position_dict is not None:
            mark = position_dict['mark']
            asset = position_dict['asset']
            quantity = position_dict['quantity']
            if asset == "OPTION":
                option_value += mark*quantity
            elif asset == "EQUITY":
                equity_value += mark*quantity
            for col in columns:
                return_dict[col].append({symbol:position_dict[col]})
    account.option_amount = option_value*100
    account.equity_amount = equity_value
    account.save(update_fields=['option_amount', 'equity_amount'])
    return JsonResponse(return_dict)
