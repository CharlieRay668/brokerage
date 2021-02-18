import sqlite3
from sqlite3 import Error
import time
from utils.TDRestAPI import Rest_Account
import _thread as thread
import pandas as pd

COLUMNS = ['symbol', 'assetType', 'assetMainType', 'cusip', 'description', 'bidPrice', 'bidSize', 'bidId', 'askPrice', 'askSize', 'askId', 'lastPrice', 'lastSize', 'lastId', 'openPrice', 'highPrice', 'lowPrice', 'bidTick', 'closePrice', 'netChange', 'totalVolume', 'quoteTimeInLong', 'tradeTimeInLong', 'mark', 'exchange', 'exchangeName', 'marginable', 'shortable', 'volatility', 'digits', 'FiftyTwoWkHigh', 'FiftyTwoWkLow', 'nAV', 'peRatio', 'divAmount', 'divYield', 'divDate', 'securityStatus', 'regularMarketLastPrice', 'regularMarketLastSize', 'regularMarketNetChange', 'regularMarketTradeTimeInLong', 'netPercentChangeInDouble', 'markChangeInDouble', 'markPercentChangeInDouble', 'regularMarketPercentChangeInDouble', 'delayed', 'openInterest', 'moneyIntrinsicValue', 'multiplier', 'strikePrice', 'contractType', 'underlying', 'expirationDay', 'expirationMonth', 'expirationYear', 'daysToExpiration', 'timeValue', 'deliverables', 'delta', 'gamma', 'theta', 'vega', 'rho', 'theoreticalOptionValue', 'underlyingPrice', 'uvExpirationType', 'lastTradingDay', 'settlementType', 'impliedYield', 'isPennyPilot']

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
            #self.db_cols
            print(update_dict)
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
    def __init__(self, rest_account):
        # VS CODE DB
        # database = r'C:\Users\charl\Desktop\BROkerage\papertrade\utils\tda_db.sqlite3'
        database = r'tda_db.sqlite3'
        self.rest_account = rest_account
        self.db_handler = DatabaseHandler()
        self.conn = self.db_handler.create_connection(database)
        
    def get_df(self, symbols):
        return self.rest_account.get_quotes(symbols)

    def loop(self):
        while True:
            for batch in self.get_symbol_batch():
                starttime = time.time()
                symbols = ','.join(batch)
                quotes = self.rest_account.get_quotes(symbols).reset_index().fillna('')
                for index, row in quotes.iterrows():
                    row = row.to_dict()
                    for key in row.keys():
                        if key not in COLUMNS:
                            row.pop(key)
                    self.db_handler.update_data(self.conn, row, row['symbol'])
                if 1.0 - ((time.time() - starttime) % 60.0) <= 0:
                    continue
                else:
                    time.sleep(1 - ((time.time() - starttime) % 60.0))
        print("thread closing...")
    
    def get_symbol_batch(self):
        #return []
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

# rest_act = Rest_Account('keys.json')
# rest_handler = RestHandler(rest_act, ['TSLA', 'AMD_020521C84.5'])
# # time.sleep(3)
# # rest_handler.add_symbol("AMD")
# # time.sleep(3)
# # rest_handler.remove_symbol("TSLA")
# # time.sleep(3)
# df = rest_handler.get_df(['TSLA', 'AMD_020521C84.5'])
# sql_command = pd.io.sql.get_schema(df.reset_index(), 'tda_data')

# con = sqlite3.connect(r'C:\Users\charl\Desktop\BROkerage\papertrade\utils\tda_db.sqlite3')
# cur = con.cursor()
# # sql = "DROP TABLE tda_data;"
# # cur.execute(sql)
# print(sql_command.strip())
# cur.execute(sql_command.strip())


# sql_command = """ CREATE TABLE IF NOT EXISTS tda_data (
#                                         id integer PRIMARY KEY,
#                                         symbol text NOT NULL,
#                                         bid_price text,
#                                         ask_price float,
#                                         last_price float,
#                                         bid_size float,
#                                         ask_size float,
#                                         ask_id char,
#                                         bid_id char,
#                                         total_volume long,
#                                         last_size float,
#                                         trade_time integer,
#                                         quote_time integer,
#                                         high_price float,
#                                         low_price float,
#                                         bid_tick char,
#                                         close_price float,
#                                         exchange_id char,
#                                         marginable boolean,
#                                         shortable boolean,
#                                         quote_day integer,
#                                         trade_day integer,
#                                         volatility float,
#                                         description text,
#                                         last_id char,
#                                         digits integer,
#                                         open_price float,
#                                         net_change float,
#                                         fiftytwo_week_high float,
#                                         fiftytwo_week_low float,
#                                         pe_ratio float,
#                                         dividend_amount float,
#                                         divident_yeild float,
#                                         nav float,
#                                         fund_price float,
#                                         exchange_name text,
#                                         dividend_date text,
#                                         regular_market_quote boolean,
#                                         regular_market_trade boolean,
#                                         regular_market_last_price float,
#                                         regular_market_last_size float,
#                                         regular_market_trade_time integer,
#                                         regular_market_trade_day integer,
#                                         regular_market_net_change float,
#                                         security_status text,
#                                         mark double,
#                                         quote_time_in_long long,
#                                         trade_time_in_long long,
#                                         regular_market_trade_time_in_long long,
#                                         open_interest integer,
#                                         money_intrinsic_value float,
#                                         expiration_year integer,
#                                         multiplier float,
#                                         strike_price float,
#                                         contract_type char,
#                                         underlying text,
#                                         expiration_month integer,
#                                         deliverables text,
#                                         time_value float,
#                                         expiration_day integer,
#                                         days_to_expiration integer,
#                                         delta float,
#                                         gamma float,
#                                         theta float,
#                                         vega float,
#                                         rho float,
#                                         theoretical_option_value float,
#                                         underlying_price double,
#                                         uv_expiration_type char
#                                     ); """
