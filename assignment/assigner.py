from users.models import User
import datetime as dt

def assign():
    position_infos = []
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
                    position_infos.append(position_info)
    return position_infos