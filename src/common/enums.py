class BaseEnum():
    _mapping = {}

    @classmethod
    def get_desc(cls, key, default='unknown'):
        return cls._mapping.get(key, default)

    @classmethod
    def get_keys(cls):
        return cls._mapping.keys()


class ResponseStatusEnum(BaseEnum):
    SUCCESS_STATUS = 0
    FAILED_STATUS = 1

    _mapping = {
        SUCCESS_STATUS: '成功',
        FAILED_STATUS: '失败'
    }


class WebSocketMessageTypeEnum(BaseEnum):
    SET_EVENT_WATCHER = 'setEventWatcher'
    ADD_JOB = 'addJob'

    _mapping = {
        SET_EVENT_WATCHER: '订阅事件',
        ADD_JOB: '添加任务'
    }


class SetEventWatcherStatusEnum(BaseEnum):
    REGISTER = 1
    CANCEL = 0

    _mapping = {
        REGISTER: '注册',
        CANCEL: '注销'
    }


class PackageNameEnum(BaseEnum):
    WECHAT = 'com.tencent.mm'

    _mapping = {
        WECHAT: '微信'
    }


class JobNameEnum(BaseEnum):
    GET_LOCAL_USER_INFO = 'get_local_user_info'
    GET_USER_LIST = 'get_user_list'
    GET_GROUP_LIST = 'get_group_list'
    SEND_IMAGE = 'send_image'
    SEND_TEXT_MESSAGE = 'send_text_message'
    RETRANSMIT_MSG = 'retransmit_msg'
    CANCEL_JOB = 'cancel_job'
    SEND_MUTI_TEXT = 'send_muti_text'
    SEND_MUTI_IMAGE = 'send_muti_image'

    _mapping = {
        GET_LOCAL_USER_INFO: '获取当前登录微信用户信息',
        GET_USER_LIST: '获取联系人列表',
        GET_GROUP_LIST: '获取群列表',
        SEND_IMAGE: '发图片消息',
        SEND_TEXT_MESSAGE: '发文字消息',
        RETRANSMIT_MSG: '转发',
        CANCEL_JOB: '取消任务',
        SEND_MUTI_TEXT: '群发文字消息',
        SEND_MUTI_IMAGE: '群发图片消息'
    }


class JobStatusEnum(BaseEnum):
    FINISH_1_STEP = 2
    FINISH = 3
    CANCEL = 4
    FAIL = 5

    _mapping = {
        FINISH_1_STEP: '两步任务, 第一步完成',
        FINISH: '完成',
        CANCEL: '取消',
        FAIL: '失败'
    }


class PushMessageType(BaseEnum):
    IMAGE = 'image'
    TEXT = 'text'

    _mapping = {
        IMAGE: '图片类型',
        TEXT: '文字类型'
    }


class ImageIsGIF(BaseEnum):
    Y = 1
    N = 0

    _mapping = {
        Y: '是',
        N: '否'
    }


class EventNameEnum(BaseEnum):
    CHAT_MESSAGE = 'chat_message'

    _mapping = {
        CHAT_MESSAGE: '有新的微信消息'
    }


class WeChatMessageContentTypeEnum(BaseEnum):
    TEXT = 0
    IMAGE = 1

    _mapping = {
        TEXT: '文字及原生表情消息',
        IMAGE: '各种图片/动图/自定义表情消息'
    }

