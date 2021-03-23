from users.models import User

def assign():
    users = User.objects.all()
    for user in users:
        positions = user.positions.objects.all()
        for position in positions:
            return position.position_info