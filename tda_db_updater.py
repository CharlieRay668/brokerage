import os
from utils.resthandler import DatabaseHandler
from utils.TDRestAPI import Rest_Account
import time

DATABASE = r'tda_db.sqlite3'
DATABASE_HANDLER = DatabaseHandler()
DATABASE_CONNECTION = DATABASE_HANDLER.create_connection(DATABASE)
rest_account = Rest_Account("keys.json")
def divide_chunks(list, n): 
    #break list into chunks of n size
    for i in range(0, len(list), n):  
        yield list[i:i + n] 

while True:
    def get_symbol_batch():
        all_quotes = [item.strip() for item in open("tickers.txt", "r").readlines()]
        return list(divide_chunks(all_quotes, 300))

        for batch in get_symbol_batch():
            starttime = time.time()
            symbols = ','.join(batch)
            quotes = rest_account.get_quotes(symbols).reset_index().fillna('')
            for index, row in quotes.iterrows():
                row = row.to_dict()
                DATABASE_HANDLER.update_data(DATABASE_CONNECTION, row, row['symbol'])
            if 1.0 - ((time.time() - starttime) % 60.0) <= 0:
                continue
            else:
                time.sleep(1 - ((time.time() - starttime) % 60.0))