"""
WSGI config for papertrade project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from utils.resthandler import RestHandler
from utils.TDRestAPI import Rest_Account

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrade.settings')

application = get_wsgi_application()

import threading
import time

REST_API = Rest_Account('keys.json')
rest_handler = REST_HANDLER = RestHandler(REST_API)

_thread = threading.Thread(target=rest_handler.loop())
_thread.setDaemon(True)
_thread.start()