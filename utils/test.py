import sqlite3
from sqlite3 import Error
import time
import utils.TDStreamingAPI as TD_Stream
from utils.TDRestAPI import Rest_Account
from utils.TDStreamingAPI import Request, ClientWebsocket, WebsocketHandler
import datetime as dt
import _thread as thread


def divide_chunks(list, n): 
    #break list into chunks of n size
    for i in range(0, len(list), n):  
        yield list[i:i + n] 

class DatabaseHandler():
    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file, check_same_thread=False)
        except Error as e:
            print(e)
        return conn

    def create_option_line(self, conn, option_line):
        """
        Create a new equity_line into the utils_data_logs_equity table
        :param conn:
        :param equity_line:
        :return: equity_line id
        """
        sql = ''' INSERT INTO utils_data_logs_option(symbol,description,bid_price,ask_price,last_price,high_price,low_price,close_price,total_volume,open_interest,volatility,quote_time,trade_time,money_intrinsic_value,quote_day,trade_day,expiration_year,multiplier,digits,open_price,bid_size,ask_size,last_size,net_change,strike_price,contract_type,underlying,expiration_month,deliverables,time_value,expiration_day,days_to_expiration,delta,gamma,theta,vega,rho,security_status,theoretical_option_value,underlying_price,uv_expiration_type,mark)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, option_line)
        conn.commit()
        return cur.lastrowid


    def create_equity_line(self, conn, equity_line):
        """
        Create a new equity_line into the utils_data_logs_equity table
        :param conn:
        :param equity_line:
        :return: equity_line id
        """
        sql = ''' INSERT INTO utils_data_logs_equity(symbol,bid_price,ask_price,last_price,bid_size,ask_size,ask_id,bid_id,total_volume,last_size,trade_time,quote_time,high_price,low_price,bid_tick,close_price,exchange_id,marginable,shortable,quote_day,trade_day,volatility,description,last_id,digits,open_price,net_change,fiftytwo_week_high,fiftytwo_week_low,pe_ratio,dividend_amount,divident_yeild,nav,fund_price,exchange_name,dividend_date,regular_market_quote,regular_market_trade,regular_market_last_price,regular_market_last_size,regular_market_trade_time,regular_market_trade_day,regular_market_net_change,security_status,mark,quote_time_in_long,trade_time_in_long,regular_market_trade_time_in_long)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, equity_line)
        conn.commit()
        return cur.lastrowid


    def check_symbol_exist_equity(self, conn, symbol):
        sql = "SELECT 1 FROM utils_data_logs_equity WHERE symbol = '%s'"%(symbol)
        cur = conn.cursor()
        cur.execute(sql)
        if cur.fetchone():
            return True
        else:
            return False

    def update_equity_row(self, conn, equity_line, symbol):
        updating_string = ''
        for key in equity_line.keys():
            if type(equity_line[key]) == str:
                value = "'" + equity_line[key] + "'"
            else:
                value = str(equity_line[key])
            if equity_line[key] is not None:
                updating_string += key+' = '+value+','
            else:
                print('NOPENOPE')
        updating_string = updating_string[:-1]
        sql = "UPDATE utils_data_logs_equity SET %s WHERE symbol = '%s'"%(updating_string, symbol)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        return cur.lastrowid

    def delete_equity_row(self, conn, symbol):
        sql = "DELETE FROM utils_data_logs_equity WHERE symbol = '%s';"%(symbol)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        return cur.lastrowid
class StreamerHandler():

    def __init__(self):
        self.db_handler = DatabaseHandler()
        database = r'C:\Users\charl\Desktop\BROkerage\papertrade\db.sqlite3'
        conn = self.db_handler.create_connection(database)

        equity_TDA_keys = "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,22,23,24,25,26,27,28,29,30,31,32,33,34,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52"
        equity_table_keys = "symbol,bid_price,ask_price,last_price,bid_size,ask_size,ask_id,bid_id,total_volume,last_size,trade_time,quote_time,high_price,low_price,bid_tick,close_price,exchange_id,marginable,shortable,quote_day,trade_day,volatility,description,last_id,digits,open_price,net_change,fiftytwo_week_high,fiftytwo_week_low,pe_ratio,dividend_amount,divident_yeild,nav,fund_price,exchange_name,dividend_date,regular_market_quote,regular_market_trade,regular_market_last_price,regular_market_last_size,regular_market_trade_time,regular_market_trade_day,regular_market_net_change,security_status,mark,quote_time_in_long,trade_time_in_long,regular_market_trade_time_in_long"

        def exit_con():
            if dt.datetime.now().minute == 5:
                return True 
            return False

        TDA_SQL_link_equity = {}
        for index, item in enumerate(equity_TDA_keys.split(',')):
            TDA_SQL_link_equity[item] = equity_table_keys.split(',')[index]


        def data_handler(data):
            for item in data['content']:
                dict_data = {}
                for TDA_key in equity_TDA_keys.split(','):
                    dict_data[TDA_key] = None
                dict_data['0'] = item['key']
                for ek in equity_TDA_keys.split(','):
                    if ek in item.keys():
                        dict_data[ek] = item[ek]
                if not self.db_handler.check_symbol_exist_equity(conn, item['key']):
                    self.db_handler.create_equity_line(conn, list(dict_data.values()))
                else:
                    cleaned_data = {}
                    for key in dict_data.keys():
                        if dict_data[key] is not None:
                            for table_keys in TDA_SQL_link_equity.keys():
                                if key == table_keys:
                                    cleaned_data[TDA_SQL_link_equity[key]] = dict_data[key]
                    self.db_handler.update_equity_row(conn, cleaned_data, item['key'])


        self.equity_client_handler = WebsocketHandler(r'C:\Users\charl\Desktop\BROkerage\papertrade\utils\keys.json', equity_TDA_keys, exit_con, data_handler, ['TSLA'])

    def add_symbol(self, symbol):
        self.equity_client_handler.add_symbol(symbol)

    def get_symbols(self):
        return self.equity_client_handler.get_symbol_keys()



# con = sqlite3.connect(r'C:\Users\charl\Desktop\BROkerage\papertrade\db.sqlite3')
# equity_talbe_dict()
# cur = con.cursor()
# print(cur.execute("""SELECT * FROM utils_data_logs_equity;"""))
# # sql_equity_command = """ CREATE TABLE IF NOT EXISTS utils_data_logs_equity (
# #                                         id integer PRIMARY KEY,
# #                                         symbol text NOT NULL,
# #                                         bid_price text,
# #                                         ask_price float,
# #                                         last_price float,
# #                                         bid_size float,
# #                                         ask_size float,
# #                                         ask_id char,
# #                                         bid_id char,
# #                                         total_volume long,
# #                                         last_size float,
# #                                         trade_time integer,
# #                                         quote_time integer,
# #                                         high_price float,
# #                                         low_price float,
# #                                         bid_tick char,
# #                                         close_price float,
# #                                         exchange_id char,
# #                                         marginable boolean,
# #                                         shortable boolean,
# #                                         quote_day integer,
# #                                         trade_day integer,
# #                                         volatility float,
# #                                         description text,
# #                                         last_id char,
# #                                         digits integer,
# #                                         open_price float,
# #                                         net_change float,
# #                                         fiftytwo_week_high float,
# #                                         fiftytwo_week_low float,
# #                                         pe_ratio float,
# #                                         dividend_amount float,
# #                                         divident_yeild float,
# #                                         nav float,
# #                                         fund_price float,
# #                                         exchange_name text,
# #                                         dividend_date text,
# #                                         regular_market_quote boolean,
# #                                         regular_market_trade boolean,
# #                                         regular_market_last_price float,
# #                                         regular_market_last_size float,
# #                                         regular_market_trade_time integer,
# #                                         regular_market_trade_day integer,
# #                                         regular_market_net_change float,
# #                                         security_status text,
# #                                         mark double,
# #                                         quote_time_in_long long,
# #                                         trade_time_in_long long,
# #                                         regular_market_trade_time_in_long long
# #                                     ); """

# # sql_option_command = """ CREATE TABLE IF NOT EXISTS utils_data_logs_options (
# #                                         id integer PRIMARY KEY,
# #                                         symbol text NOT NULL,
# #                                         description text,
# #                                         bid_price text,
# #                                         ask_price float,
# #                                         last_price float,
# #                                         high_price float,
# #                                         low_price float,
# #                                         close_price float,
# #                                         total_volume long,
# #                                         open_interest integer,
# #                                         volatility float,
# #                                         quote_time long,
# #                                         trade_time long,
# #                                         money_intrinsic_value float,
# #                                         quote_day integer,
# #                                         trade_day integer,
# #                                         expiration_year integer,
# #                                         multiplier float,
# #                                         digits integer,
# #                                         open_price float,
# #                                         bid_size float,
# #                                         ask_size float,
# #                                         last_size float,
# #                                         net_change float,
# #                                         strike_price float,
# #                                         contract_type char,
# #                                         underlying text,
# #                                         expiration_month integer,
# #                                         deliverables text,
# #                                         time_value float,
# #                                         expiration_day integer,
# #                                         days_to_expiration integer,
# #                                         delta float,
# #                                         gamma float,
# #                                         theta float,
# #                                         vega float,
# #                                         rho float,
# #                                         security_status text
# #                                         theoretical_option_value float,
# #                                         underlying_price double,
# #                                         uv_expiration_type char,
# #                                         mark double
# #                                     ); """
# # print(sql_option_command.strip())
# # cur.execute(sql_option_command.strip())

# # for row in cur.execute('SELECT * FROM main_equityposition'):
# #     print(row)

# con.close()