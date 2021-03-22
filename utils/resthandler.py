import sqlite3
from sqlite3 import Error
import time
from utils.TDRestAPI import Rest_Account
import _thread as thread
import pandas as pd

def divide_chunks(list, n): 
    #break list into chunks of n size
    for i in range(0, len(list), n):  
        yield list[i:i + n] 

class DatabaseHandler():
    def __init__(self):
        self.db_cols = ['symbol', 'assetType', 'assetMainType', 'cusip', 'description', 'bidPrice', 'bidSize', 'bidId', 'askPrice', 'askSize', 'askId', 'lastPrice', 'lastSize', 'lastId', 'openPrice', 'highPrice', 'lowPrice', 'bidTick', 'closePrice', 'netChange', 'totalVolume', 'quoteTimeInLong', 'tradeTimeInLong', 'mark', 'exchange', 'exchangeName', 'marginable', 'shortable', 'volatility', 'digits', 'FiftyTwoWkHigh', 'FiftyTwoWkLow', 'nAV', 'peRatio', 'divAmount', 'divYield', 'divDate', 'securityStatus', 'regularMarketLastPrice', 'regularMarketLastSize', 'regularMarketNetChange', 'regularMarketTradeTimeInLong', 'netPercentChangeInDouble', 'markChangeInDouble', 'markPercentChangeInDouble', 'regularMarketPercentChangeInDouble', 'delayed', 'openInterest', 'moneyIntrinsicValue', 'multiplier', 'strikePrice', 'contractType', 'underlying', 'expirationDay', 'expirationMonth', 'expirationYear', 'daysToExpiration', 'timeValue', 'deliverables', 'delta', 'gamma', 'theta', 'vega', 'rho', 'theoreticalOptionValue', 'underlyingPrice', 'uvExpirationType', 'lastTradingDay', 'settlementType', 'impliedYield', 'isPennyPilot']


    def create_connection(self, db_file):
        """ create a database connection to the SQLite database specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file, check_same_thread=False)
        except Error as e:
            print(e)
        return conn

    def create_new_line(self, conn, equity_line):
        """
        Create a new line into the tda_data table
        :param conn:
        :param equity_line:
        :return: equity_line id
        """
        sql = ''' INSERT INTO tda_data('''+','.join(self.db_cols)+''')
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, equity_line)
        conn.commit()
        return cur.lastrowid


    def check_symbol_exist(self, conn, symbol):
        sql = "SELECT 1 FROM tda_data WHERE symbol = '%s'"%(symbol)
        cur = conn.cursor()
        cur.execute(sql)
        if cur.fetchone():
            return True
        else:
            return False

    def update_cells(self, conn, update_dict, symbol):
        updating_string = ''
        for key in update_dict.keys():
            if type(update_dict[key]) == str:
                value = "'" + update_dict[key] + "'"
            else:
                value = str(update_dict[key])
            if update_dict[key] is not None:
                updating_string += key+' = '+value+','
            else:
                print('NOPENOPE')
        updating_string = updating_string[:-1]
        sql = "UPDATE tda_data SET %s WHERE symbol = '%s'"%(updating_string, symbol)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        return cur.lastrowid

    # def delete_equity_row(self, conn, symbol):
    #     sql = "DELETE FROM utils_data_logs_equity WHERE symbol = '%s';"%(symbol)
    #     cur = conn.cursor()
    #     cur.execute(sql)
    #     conn.commit()
    #     return cur.lastrowid

    def update_data(self, conn, update_dict, symbol):
        if self.check_symbol_exist(conn, symbol):
            self.update_cells(conn, update_dict, symbol)
        else:
            keys = self.db_cols
            update_line = []
            for key in keys:
                try:
                    update_line.append(update_dict[key])
                except:
                    update_line.append(None)
            self.create_new_line(conn, update_line)

    def get_all_symbols(self, conn):
        sql = "SELECT symbol FROM tda_data"
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()


class RestHandler():
    def __init__(self, rest_account=None):
        # VS CODE DB
        # database = r'C:\Users\charl\Desktop\BROkerage\papertrade\utils\tda_db.sqlite3'
        database = r'tda_db.sqlite3'
        self.rest_account = rest_account
        self.db_handler = DatabaseHandler()
        self.conn = self.db_handler.create_connection(database)

    def get_df(self, symbols):
        return self.rest_account.get_quotes(symbols)
    
    def get_symbol_batch(self):
        all_quotes = [item.strip() for item in open("tickers.txt", "r").readlines()]
        return list(divide_chunks(all_quotes, 300))
    
    def add_symbol(self, symbol):
        try:
            if symbol not in [item.strip() for item in open("tickers.txt", "r").readlines()]:
                open("tickers.txt", "a+").write(str(symbol)+"\n")
                return True
            return False
        except:
            return False

    def remove_symbol(self, symbol):
        if symbol in self.all_quotes:
            self.all_quotes.remove(symbol)
            return True
        return False

    def get_symbols(self):
        return [item.strip() for item in open("tickers.txt", "r").readlines()]
    
    def clear_symbols(self):
        tickers = open("tickers.txt", "w")
        tickers.close()
        return True