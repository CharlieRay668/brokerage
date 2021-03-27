import requests


orders = [[100, 'str', 45.0]]
username = "JoMama"
underlying = "MAXR"
account_id = 3
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
        print(response.text)

make_order(orders, username, underlying, account_id)