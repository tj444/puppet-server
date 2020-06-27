from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from manager.consumers import WebSocketConsumer


application = ProtocolTypeRouter({
    "websocket": URLRouter([
        url(r"^websocket$", WebSocketConsumer),
    ])
})
