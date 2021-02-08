"""
ASGI config for papertrade project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os


# from django.core.asgi import get_asgi_application
# from custom_websocket.middleware import websockets

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrade.settings')
# application = get_asgi_application()
# application = websockets(application)

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrade.settings')

application = get_asgi_application()