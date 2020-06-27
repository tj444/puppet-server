from .enums import EventNameEnum, WeChatMessageContentTypeEnum

# 监听的事件
WATCH_EVENTS = [
    EventNameEnum.CHAT_MESSAGE
]

# 允许转发的微信消息类型
ALLOWED_RETRANSMIT_MESSAGE_TYPES = [
    WeChatMessageContentTypeEnum.TEXT,
    WeChatMessageContentTypeEnum.IMAGE
]
