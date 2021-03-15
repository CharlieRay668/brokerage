from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
import datetime as dt
from pytz import timezone
import pandas as pd
import json
from main.forms import CreateNewBuyPosition, CreateNewSellPosition
from main.models import Position
from utils.TDRestAPI import Rest_Account
from utils.resthandler import RestHandler, DatabaseHandler
import time
import uuid

REST_API = Rest_Account('keys.json')

DATABASE = r'tda_db.sqlite3'
DATABASE_HANDLER = DatabaseHandler()
DATABASE_CONNECTION = DATABASE_HANDLER.create_connection(DATABASE)
REST_HANDLER = RestHandler(REST_API)

def trade(response, act_id):
    if response.method == "POST":
        return redirect("/trade/"+str(act_id)+"/" + str(response.POST['searchBar']))
    data = pd.read_csv('utils/stock_symbols.csv')
    symbols = data['Symbol'].to_list()
    company_names = data['Name'].to_list()
    for item in company_names:
        symbols.append(item)
    symbols = json.dumps(symbols)
    return render(response, "trade/trade.html", {'autofill_symbols': symbols,})

def tradesymbol(response, symbol, act_id, buy_sell="buy"):
    user = response.user
    fmt = "%m/%d/%Y, %I:%M:%S"
    eastern = timezone('US/Eastern')
    curr_time = dt.datetime.now(eastern).strftime(fmt)
    # if not symbol in REST_HANDLER.get_symbols():
    #     REST_HANDLER.add_symbol(symbol)
    #     time.sleep(2)
    added = False
    while not DATABASE_HANDLER.check_symbol_exist(DATABASE_CONNECTION, symbol):
        if not added:
            REST_HANDLER.add_symbol(symbol)
            added = True
        time.sleep(1)
    if response.method == "POST":
        if buy_sell == "buy":
            form = CreateNewBuyPosition(response.POST)
        else:
            form = CreateNewSellPosition(response.POST)
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
                    added = True
                    REST_HANDLER.add_symbol(symbol)
                time.sleep(1)
            # If we are selling/buying we will go for either the bid or the ask price
            if quantity > 0:
                sql = "SELECT askPrice from tda_data WHERE symbol ='%s'"%(symbol)
            elif quantity < 0:  
                sql = "SELECT bidPrice from tda_data WHERE symbol ='%s'"%(symbol)
            else:
                # If the quantity is 0 just return the page, things are being weird.
                return render(response, "trade/tradesymbol.html", {'stock_symbol':symbol, 'curr_time':curr_time, "form":form})
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
            # Create and save the new position.
            new_position = Position(position_id=position_id, symbol=symbol, quantity=quantity, fill_price=fill_price, position_info=position_info, order_action=action, order_type=order_type, order_expiration=order_expiration, order_execution_date=order_execution_date, limit_price=limit_price)
            new_position.save()
            account = user.accounts.get(id=act_id)
            position_dict = position_info[0]
            asset_type = position_dict['assetType']
            if asset_type == "EQUITY":
                account.cash_amount -= quantity*fill_price
            elif asset_type == "OPTION":
                account.cash_amount -= (quantity*fill_price)*100
            account.acct_positions.add(new_position)
            account.save(update_fields=['option_amount', 'equity_amount', 'cash_amount'])
            user.positions.add(new_position)
            return redirect('/accounts/view/'+str(act_id)+'/')
    else:
        if buy_sell == "buy":
            form = CreateNewBuyPosition()
        else:
            form = CreateNewSellPosition()
    return render(response, "trade/tradesymbol.html", {'stock_symbol':symbol, 'curr_time':curr_time, "form":form})
    
def tradesymbol_chain(response, symbol, act_id):
    fmt = "%m/%d/%Y, %I:%M:%S"
    eastern = timezone('US/Eastern')
    curr_time = dt.datetime.now(eastern).strftime(fmt)
    chain = REST_API.get_options_chain(symbol, time_delta=720, strike_count=1, contract_type='CALL')
    expiries = chain['description'].to_list()
    expiries = [' '.join(expiry.split(' ')[:4]) for expiry in expiries]
    expiries = json.dumps(expiries)
    return render(response, "trade/tradesymbolchain.html", {'stock_symbol':symbol, 'curr_time':curr_time, "chain":chain, "expiries":expiries})