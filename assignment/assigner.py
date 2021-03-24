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
            position_info = position.position_info[0]
            if position_info['assetType'] == "OPTION":
                expiration_day = position_info['expirationDay']
                expiration_month = position_info['expirationMonth']
                expiration_year = position_info['expirationYear']
                expiration = dt.date(expiration_year, expiration_month, expiration_day)
                now = dt.date.today()
                if now > expiration:
                    total_positions.append(position)
                    underlyings.append(position_info['underlying'])
    quotes = REST_API.get_quotes(underlyings)
    for position in total_positions:
        strike_price = position.position_info[0]['strikePrice']
    return quotes