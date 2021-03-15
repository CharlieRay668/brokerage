import os
from utils.resthandler import DatabaseHandler
from utils.TDRestAPI import Rest_Account
import time


COLUMNS = ['symbol', 'assetType', 'assetMainType', 'cusip', 'description', 'bidPrice', 'bidSize', 'bidId', 'askPrice', 'askSize', 'askId', 'lastPrice', 'lastSize', 'lastId', 'openPrice', 'highPrice', 'lowPrice', 'bidTick', 'closePrice', 'netChange', 'totalVolume', 'quoteTimeInLong', 'tradeTimeInLong', 'mark', 'exchange', 'exchangeName', 'marginable', 'shortable', 'volatility', 'digits', 'FiftyTwoWkHigh', 'FiftyTwoWkLow', 'nAV', 'peRatio', 'divAmount', 'divYield', 'divDate', 'securityStatus', 'regularMarketLastPrice', 'regularMarketLastSize', 'regularMarketNetChange', 'regularMarketTradeTimeInLong', 'netPercentChangeInDouble', 'markChangeInDouble', 'markPercentChangeInDouble', 'regularMarketPercentChangeInDouble', 'delayed', 'openInterest', 'moneyIntrinsicValue', 'multiplier', 'strikePrice', 'contractType', 'underlying', 'expirationDay', 'expirationMonth', 'expirationYear', 'daysToExpiration', 'timeValue', 'deliverables', 'delta', 'gamma', 'theta', 'vega', 'rho', 'theoreticalOptionValue', 'underlyingPrice', 'uvExpirationType', 'lastTradingDay', 'settlementType', 'impliedYield', 'isPennyPilot']

DATABASE = r'tda_db.sqlite3'
DATABASE_HANDLER = DatabaseHandler()
DATABASE_CONNECTION = DATABASE_HANDLER.create_connection(DATABASE)
rest_account = Rest_Account("keys.json")
def divide_chunks(list, n): 
    #break list into chunks of n size
    for i in range(0, len(list), n):  
        yield list[i:i + n] 

def get_symbol_batch():
    all_quotes = [item.strip() for item in open("tickers.txt", "r").readlines()]
    return list(divide_chunks(all_quotes, 300))
    
while True:
        for batch in get_symbol_batch():
            try:
                starttime = time.time()
                symbols = ','.join(batch)
                quotes = rest_account.get_quotes(symbols).reset_index().fillna('')
                for index, row in quotes.iterrows():
                    row = row.to_dict()
                    true_dict = {}
                    for key in row.keys():
                        if key in COLUMNS:
                            true_dict[key] = row[key]
                    DATABASE_HANDLER.update_data(DATABASE_CONNECTION, true_dict, true_dict['symbol'])
                if 5.0 - ((time.time() - starttime) % 60.0) <= 0:
                    continue
                else:
                    time.sleep(5 - ((time.time() - starttime) % 60.0))
            except:
                time.sleep(3)