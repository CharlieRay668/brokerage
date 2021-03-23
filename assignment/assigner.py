from users.models import User

def assign():
    users = User.objects.all()
    for user in users:
        positions = user.positions.all()
        for position in positions:
            position_info = position.position_info[0]
            if position_info['assetType'] == "OPTION":
                return position.position_info