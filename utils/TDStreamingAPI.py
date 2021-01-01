import urllib
import json
import requests
import dateutil.parser
import datetime
from datetime import datetime
import time
import websocket
import threading
import _thread as thread
from utils.TDRestAPI import Rest_Account

def format_header(access_token):
    return {'Authorization': "Bearer {}".format(access_token)}

def unix_time_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000.0

def get_user_principals(key_file_name):
    account = Rest_Account(key_file_name)
    endpoint = "https://api.tdameritrade.com/v1/userprincipals"

    headers = format_header(account.update_access_token())

    params = {'fields':'streamerSubscriptionKeys,streamerConnectionInfo'}

    content = requests.get(url = endpoint, params = params, headers = headers)
    return content.json()

def get_login_request(userPrincipalsResponse):
    tokenTimeStamp = userPrincipalsResponse['streamerInfo']['tokenTimestamp']
    date = dateutil.parser.parse(tokenTimeStamp, ignoretz = True)
    tokenTimeStampAsMs = unix_time_millis(date)
    credentials = {"userid": userPrincipalsResponse['accounts'][0]['accountId'],
                "token": userPrincipalsResponse['streamerInfo']['token'],
                "company": userPrincipalsResponse['accounts'][0]['company'],
                "segment": userPrincipalsResponse['accounts'][0]['segment'],
                "cddomain": userPrincipalsResponse['accounts'][0]['accountCdDomainId'],
                "usergroup": userPrincipalsResponse['streamerInfo']['userGroup'],
                "accesslevel":userPrincipalsResponse['streamerInfo']['accessLevel'],
                "authorized": "Y",
                "timestamp": int(tokenTimeStampAsMs),
                "appid": userPrincipalsResponse['streamerInfo']['appId'],
                "acl": userPrincipalsResponse['streamerInfo']['acl'] }

    login_request = {"requests": [{"service": "ADMIN",
                                "requestid": "0",  
                                "command": "LOGIN",
                                "account": userPrincipalsResponse['accounts'][0]['accountId'],
                                "source": userPrincipalsResponse['streamerInfo']['appId'],
                                "parameters": {"credential": urllib.parse.urlencode(credentials),
                                                "token": userPrincipalsResponse['streamerInfo']['token'],
                                                "version": "1.0"}}]}
    return json.dumps(login_request)
    

def get_data_request(requests, request_id = 1):
    services = []
    for request in requests:
        services.append({'service': request.service,
                         'requestid': request_id,
                         'command': request.command,
                         'account': request.account,
                         'source': request.source,
                         'parameters': request.params})
        request_id += 1
    data_request = {'requests': services}
    return json.dumps(data_request), request_id


class Request():
    def __init__(self, service, command, user_principals, params):
        self.service = service
        self.command = command
        self.account = user_principals['accounts'][0]['accountId']
        self.source = user_principals['streamerInfo']['appId']
        self.params = params

class ClientWebsocket():
    def __init__(self, login, data, exit_condition, user_principals, enable_trace, data_handler):
        self.login = login
        self.data = data
        self.exit_condition = exit_condition
        self.user_principals = user_principals
        self.data_handler = data_handler
        self.ready = False
        uri = "wss://" + self.user_principals['streamerInfo']['streamerSocketUrl'] + "/ws"
        websocket.enableTrace(enable_trace)
        self.ws = websocket.WebSocketApp(uri,
                                on_message = lambda ws,msg: self.on_message(ws, msg),
                                on_error = lambda ws,msg: self.on_error(ws, msg),
                                on_close = lambda ws: self.on_close(ws),
                                on_open = lambda ws: self.on_open(ws))

    def send_message(self, message):
        #print(message)
        self.ws.send(message)

    def check_close(self):
        if self.exit_condition():
            self.ws.close()
            print("thread terminating...")

    def on_message(self, ws, message):
        message_decoded = json.loads(message)
        # if 'response' in message_decoded.keys():
        #     self.ready = True
        if 'notify' in message_decoded.keys():
            print(message_decoded)
        if 'data' in message_decoded.keys():
            data = message_decoded['data'][0]
            self.data_handler(data)
            self.check_close()
            return data
        self.check_close()
        return None

    def on_error(self, ws, error):
        print(error, ' errors')
        return error

    def on_close(self, ws):
        print("### closed ###")
        return True

    def on_open(self, ws):
        def run(*args):
            ws.send(self.login)
            time.sleep(1)
            if type(self.data) is not None:
                ws.send(self.data)
            self.check_close()
            self.ready = True
        thread.start_new_thread(run, ())

    def get_websocket(self):
        return self.ws

class WebsocketHandler():
    def __init__(self, json_location, fields, exit_con, data_handler, symbol_keys=[], enable_trace=True, request_type='QUOTE'):
        self.symbol_keys = symbol_keys
        self.exit_con = exit_con
        self.data_handler = data_handler
        if len(self.symbol_keys) == 0:
            self.symbol_keys.append('SPY')
        self.user_principals = get_user_principals(json_location)
        self.fields = fields
        self.request_type = request_type
        temp_requests = [Request(self.request_type, 'SUBS', self.user_principals, {"keys": ','.join(self.symbol_keys), "fields": self.fields})]
        login_encoded = get_login_request(self.user_principals)
        temp_data_encoded, self.request_id = get_data_request(temp_requests)
        self.client = ClientWebsocket(login_encoded, temp_data_encoded, exit_con, self.user_principals, enable_trace, data_handler)
        self.ws = self.client.get_websocket()
        thread.start_new_thread(self.ws.run_forever, ())
        while not self.client.ready:
            time.sleep(1)
    
    def add_symbol(self, symbol):
        self.symbol_keys.append(symbol)
        socket_request, self.request_id = get_data_request([Request(self.request_type, 'SUBS', self.user_principals, {"keys": ','.join(self.symbol_keys),"fields": self.fields})], self.request_id)
        self.client.send_message(socket_request)

    def get_symbol_keys(self):
        return self.symbol_keys
