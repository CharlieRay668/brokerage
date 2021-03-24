from users.models import User
from main.models import Position
import datetime as dt
from utils.TDRestAPI import Rest_Account

REST_API = Rest_Account('keys.json')
def assign():
    total_positions = []
    underlyings = []
    users = User.objects.all()
    for user in users:
        positions = user.positions.all()
        for position in positions:
            if type(position.position_info) is list:
                position_info = position.position_info[0]
            else:
                position_info = position.position_info
            if position_info['assetType'] == "OPTION":
                expiration_day = position_info['expirationDay']
                expiration_month = position_info['expirationMonth']
                expiration_year = position_info['expirationYear']
                expiration = dt.date(int(expiration_year), int(expiration_month), int(expiration_day))
                now = dt.date.today()
                if now > expiration:
                    total_positions.append(position)
                    underlyings.append(position_info['underlying'])
    quotes = REST_API.get_quotes(underlyings)
    for position in total_positions:
        if type(position.position_info) is list:
            position_info = position.position_info[0]
        else:
            position_info = position.position_info
        strike_price = position_info['strikePrice']
        underlying = position_info['underlying']
        returns = []
        for index, row in quotes():
            returns.append((index, row))
    return returns