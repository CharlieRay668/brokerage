from django.urls import resolve
from .connection import WebSocket

def websockets(app):
    async def asgi(scope, receive, send):
        print(scope, receive, send)
        if scope["type"] == "websocket":
            match = resolve(scope["raw_path"].decode("utf-8"))
            await match.func(WebSocket(scope, receive, send), *match.args, **match.kwargs)
            return
        await app(scope, receive, send)
    return asgi()