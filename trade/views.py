from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import datetime as dt
from pytz import timezone
import pandas as pd
import json
from main.forms import CreateNewBuyPosition, CreateNewSellPosition
from main.models import Position
from utils.TDRestAPI import Rest_Account
import time
import uuid

REST_API = Rest_Account('keys.json')


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
    if response.method == "POST":
        if buy_sell == "buy":
            form = CreateNewBuyPosition(response.POST)
        else:
            form = CreateNewSellPosition(response.POST)
        if form.is_valid():
            quote = REST_API.get_quotes(symbol)
            if quote is None:
                return HttpResponse("Invalid Symbol", status=304)
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
            quantity = float(cleaned['quantity'])
            action = cleaned['action']
            # if the action was 2, (sell) flip quantity sign
            if action == "2":
                quantity = quantity*-1
            added = False
            # If we are selling/buying we will go for either the bid or the ask price
            # Get our fill price for this specific order.
            if quantity > 0:
                fill_price = quote['askPrice']
            elif quantity < 0:  
                fill_price = quote['bidPrice']
            else:
                # If the quantity is 0 just return the page, things are being weird.
                return render(response, "trade/tradesymbol.html", {'stock_symbol':symbol, 'curr_time':curr_time, "form":form})
            order_type = cleaned['order_type']
            order_expiration = cleaned['order_expiration']
            order_execution_date = dt.datetime.now(eastern)
            # If our limit price is none, ie market price, set it to -999 to avoid db conflicts.
            limit_price = cleaned['limit_price']
            if limit_price is None:
                limit_price = -999
            # Grab the snapshot of the market conditions, make dataframe into a dict and then save it in database.
            position_info = quote.to_dict()
            # Create and save the new position.
            new_position = Position(position_id=position_id, symbol=symbol, quantity=quantity, fill_price=fill_price, position_info=position_info, order_action=action, order_type=order_type, order_expiration=order_expiration, order_execution_date=order_execution_date, limit_price=limit_price)
            new_position.save()
            # Add he position to the correnct account, edit the cash amount in the account accordingly.
            account = user.accounts.get(id=act_id)
            asset_type = quote['assetType']
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