from users.models import User
from main.models import Position
import datetime as dt
import requests
from utils.TDRestAPI import Rest_Account
from pytz import timezone

REST_API = Rest_Account('keys.json')
eastern = timezone('US/Eastern')

def make_order(orders, username, underlying, account_id):
    responses = []
    for order in orders:
        quantity = order[0]
        order_type = order[1]
        headers = {"apikey": "charliekey"}
        if quantity > 0:
            action = 1
        else:
            action = 2
        
        payload = {
            "username": username,
            "symbol": underlying,
            "quantity": abs(quantity),
            "action": action,
            "order_type": 2,
            "order_expiration": 1,
            "account_id": account_id, 
        }
        if order_type == "str":
            payload['price_override'] = order[2]
        response = requests.post("https://rillionbrokerage.com/api/create/", headers=headers, data=payload, verify=True)
        responses.append(response.status_code)
    return responses

def assign():
    total_positions = []
    underlyings = []
    users = User.objects.all()
    for user in users:
        username = user.username
        accounts = user.accounts.all()
        for account in accounts:
            account_id = account.id
            positions = account.acct_positions.all()
            for position in positions:
                if type(position.position_info) is list:
                    position_info = position.position_info[0]
                else:
                    position_info = position.position_info
                if position_info['assetType'] == "OPTION":
                    if not "expired" in position_info.keys():
                        expiration_day = position_info['expirationDay']
                        expiration_month = position_info['expirationMonth']
                        expiration_year = position_info['expirationYear']
                        expiration = dt.date(int(expiration_year), int(expiration_month), int(expiration_day))
                        now = dt.date.today()
                        if now > expiration:
                            total_positions.append((username, account_id, position))
                            underlyings.append(position_info['underlying'])
    quotes = REST_API.get_quotes(underlyings)
    true_account_id = None
    for username, account_id, position in total_positions:
        if type(position.position_info) is list:
            position_info = position.position_info[0]
        else:
            position_info = position.position_info
        contract_type = position_info['contractType']
        strike_price = position_info['strikePrice']
        underlying = position_info['underlying']
        returns = []
        for symbol, row in quotes.iterrows():
            if symbol == underlying:
                market_price = row['mark']
        quantity = position.quantity
        if contract_type == "P":
            if strike_price > market_price:
                if quantity > 0:
                    # User held put contract, add @ market then remove shares @ strike price (net gain)
                    orders = [[100*(abs(quantity)), "mkt"],[-100*(abs(quantity)), "str", strike_price]]
                elif quantity < 0:
                    # User sold put contract, add shares @ strike price (net loss)
                    orders = [[100*(abs(quantity)), 'str', strike_price]]
        else:
            if strike_price < market_price:
                if quantity > 0:
                    # User held call contract, add shares @ strike price (net gain)
                    orders = [[100*(abs(quantity)), 'str', strike_price]]
                elif quantity < 0:
                    # User sold call contract, add @ market then remove shares @ strike price (net loss)
                    orders = [[100*(abs(quantity)), "mkt"],[-100*(abs(quantity)), "str", strike_price]]
        responses = make_order(orders, username, underlying, account_id)
        position_id = position.position_id
        symbol = position.symbol
        quantity = position.quantity*-1
        fill_price = 0
        if type(position.position_info) is list:
            position_info = position.position_info[0]
        else:
            position_info = position.position_info
        position_info["expired"] = True
        if quantity > 0:
            action = 1
        else:
            action = 2
        order_type = 1
        order_expiration = 1
        order_execution_date = dt.datetime.now(eastern)
        limit_price = -999
        new_position = Position(position_id=position_id, symbol=symbol, quantity=quantity, fill_price=fill_price, position_info=position_info, order_action=action, order_type=order_type, order_expiration=order_expiration, order_execution_date=order_execution_date, limit_price=limit_price)
        new_position.save()
        account.acct_positions.add(new_position)
        user.positions.add(new_position)
    return responses