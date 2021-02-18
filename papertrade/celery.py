import os
from utils.resthandler import DatabaseHandler
from utils.TDRestAPI import Rest_Account
from celery import Celery
import time
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrade.settings')

app = Celery('papertrade')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


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

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls update_tda_data('hello') every 2 seconds.
    sender.add_periodic_task(2.0, update_tda_data.s("hello"))

@app.task
def update_tda_data(arg):
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