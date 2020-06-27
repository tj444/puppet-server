import logging
from channels.generic.websocket import JsonWebsocketConsumer
from .cache import (
    DEVICE_WEBSOCKET_HANDLER_MAP,
    DEVICE_FRIENDS_MAP,
    DEVICE_GROUPS_MAP
)
from .handler import WebSocketHandler


logger = logging.getLogger('django')


class WebSocketConsumer(JsonWebsocketConsumer):
    
    def connect(self):
        headers = dict(self.scope['headers'])
        device_id = headers.get(b'deviceid')
        self.device_id = device_id.decode() if device_id else device_id
        self.accept()
        ws_handler = WebSocketHandler(self)
        DEVICE_WEBSOCKET_HANDLER_MAP[self.device_id] = ws_handler
        ws_handler.connect_handler()

    def receive_json(self, content):
        ws_handler = DEVICE_WEBSOCKET_HANDLER_MAP.get(self.device_id)
        ws_handler.receive_handler(content)

    def disconnect(self, code):
        logger.info('[websocket] {} disconnect websocket'.format(self.device_id))
        device_id = self.device_id
        if device_id in DEVICE_WEBSOCKET_HANDLER_MAP:
            del DEVICE_WEBSOCKET_HANDLER_MAP[device_id]
        if device_id in DEVICE_FRIENDS_MAP:
            del DEVICE_FRIENDS_MAP[device_id]
        if device_id in DEVICE_GROUPS_MAP:
            del DEVICE_GROUPS_MAP[device_id]

