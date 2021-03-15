from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse

from .forms import CreateAccount
from .models import Account
from utils.resthandler import RestHandler, DatabaseHandler
from utils.TDRestAPI import Rest_Account
from main.views import calc_df, get_position_dict

import pandas as pd
import time

REST_API = Rest_Account('keys.json')
REST_HANDLER = RestHandler(REST_API)
DATABASE = r'tda_db.sqlite3'
DATABASE_HANDLER = DatabaseHandler()
DATABASE_CONNECTION = DATABASE_HANDLER.create_connection(DATABASE)

def create(response):
    if response.method == "POST":
        form = CreateAccount(response.POST)
        if form.is_valid():
            account_name = response.POST['name']
            cash_amount = response.POST['cash_amount']
            user = response.user
            new_account = Account(user=user, name=account_name, cash_amount=cash_amount, equity_amount=0, option_amount=0, short_equity_amount=0, short_option_amount=0)
            new_account.save()
            user.accounts.add(new_account)
    form = CreateAccount()
    return render(response, "trade_accounts/create.html", {'form':form})

def prompt_view(response):
    user = response.user
    accounts = user.accounts.all()
    if len(accounts) == 0:
        return redirect("accounts/create/")
    if len(accounts) == 1:
        account = accounts[0]
        return redirect("/accounts/view/"+str(account.id)+"/")
    return render(response, "trade_accounts/prompt_view.html", {"accounts": accounts})

def view(response, act_id):
    # USer and account definition
    user = response.user
    accounts = user.accounts.all()
    account = user.accounts.get(id=act_id)
    positions = account.acct_positions.all()
    account_balance = account.option_amount + account.cash_amount
    # Index Change Handling
    indexes = ['SPY', 'DIA', 'QQQ']
    index_prices = []
    for index in indexes:
        added = False
        # Check to see if the is in the database, if its not, add it and wait.
        while not DATABASE_HANDLER.check_symbol_exist(DATABASE_CONNECTION, index):
            if not added:
                added = True
                REST_HANDLER.add_symbol(index)
            time.sleep(1)
        cur = DATABASE_CONNECTION.cursor()
        if DATABASE_HANDLER.check_symbol_exist(DATABASE_CONNECTION, index):
            sql = "SELECT mark,closePrice from tda_data WHERE symbol ='%s'"%(index)
            cur.execute(sql)
            data = cur.fetchall()[0]
            mark = round(data[0],2)
            close_price = round(data[1],2)
            change = mark-close_price
            index_prices.append((change/mark)*100)
    average = round(sum(index_prices)/3,2)
    if average >= 0:
        average_dir = "up"
    else:
        average_dir = "down"

    # Position Handling
    if len(positions) == 0:
        return render(response, "trade_accounts/view.html", {'account': account, 'accounts': accounts, 'account_balance': account_balance, 'positions': positions, 'average':average, 'average_dir':average_dir}) 
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
    
    return render(response, "trade_accounts/view.html", {'account': account, 'accounts': accounts, 'account_balance': account_balance, 'positions': positions, 'average':average, 'average_dir':average_dir})
