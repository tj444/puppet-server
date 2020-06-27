import json
import time
import threading
import logging
from threading import Timer
from django.conf import settings
from .cache import (
    DEVICE_WEBSOCKET_HANDLER_MAP,
    DEVICE_FRIENDS_MAP,
    DEVICE_GROUPS_MAP
)
from common.enums import (
    PackageNameEnum,
    JobNameEnum,
    WebSocketMessageTypeEnum,
    SetEventWatcherStatusEnum,
    JobStatusEnum,
    PushMessageType,
    EventNameEnum,
    WeChatMessageContentTypeEnum,
)
from common.utils import generate_request_id, generate_job_id
from common.common import WATCH_EVENTS, ALLOWED_RETRANSMIT_MESSAGE_TYPES


logger = logging.getLogger('django')


class WebSocketHandler():
    ''' 目前已实现
        1. 获取当前微信信息
        2. 订阅事件
        3. 获取联系人列表
        4. 获取群列表
        5. 发送图片
        6. 发送文字
        7. 转发
        8. 取消消息
        9. 群发文字消息
        10. 群发图片消息
        后续有其他消息格式，继续定义就好了
    '''
    
    def __init__(self, ws):
        self.ws = ws

    def connect_handler(self):
        ''' 创建连接时的处理操作
        1. 获取当前微信信息
        2. 订阅事件
        3. 获取联系人列表
        4. 获取群列表
        '''
        logger.info('[websocket] {} connect websocket success'.format(self.ws.device_id))
        self.get_local_user_info()
        for watch_event in WATCH_EVENTS:
            self.set_event_watcher(watch_event)
        self.get_user_list()
        self.get_group_list()
        self.timer()

    def timer(self):
        timer = Timer(settings.TIMER_TIMES, self.timer_handler)
        timer.start()

    def timer_handler(self):
        self.get_user_list()
        self.get_group_list()
        self.timer()

    def _send_json(self, request_body):
        logger.info('[websocket] send message to {}: {}'.format(self.ws.device_id, request_body))
        self.ws.send_json(request_body)

    def receive_handler(self, content):
        logger.info('[websocket] receive message from {}: {}'.format(self.ws.device_id, content))

    def _get_request_body(self, message_type, data):
        return {
            'request_id': generate_request_id(),
            'type': message_type,
            'data': data
        }

    def _get_set_event_watcher_request_data(self, event_name, package_name, watcher_status):
        return {
            'event_name': event_name,
            'package_name': package_name,
            'callback': settings.EVENT_CALLBACK,
            'watcher_status': watcher_status
        }

    def _get_add_job_request_data(self, package_name, job_name, job_data):
        return {
            'job_id': generate_job_id(),
            'package_name': package_name,
            'callback': settings.JOB_RESULT_CALLBACK,
            'job_name': job_name,
            'job_data': job_data
        }

    def set_event_watcher(self, event_name):
        request_data = self._get_set_event_watcher_request_data(
            event_name,
            PackageNameEnum.WECHAT,
            SetEventWatcherStatusEnum.REGISTER
        )
        request_body = self._get_request_body(WebSocketMessageTypeEnum.SET_EVENT_WATCHER, request_data)
        self._send_json(request_body)

    def get_local_user_info(self):
        ''' 当前登录微信号信息
        '''
        job_data = {}
        request_data = self._get_add_job_request_data(
            PackageNameEnum.WECHAT,
            JobNameEnum.GET_LOCAL_USER_INFO,
            job_data
        )
        request_body = self._get_request_body(WebSocketMessageTypeEnum.ADD_JOB, request_data)
        self._send_json(request_body)

    def get_user_list(self):
        ''' 联系人列表
        '''
        job_data = {}
        request_data = self._get_add_job_request_data(
            PackageNameEnum.WECHAT,
            JobNameEnum.GET_USER_LIST,
            job_data
        )
        request_body = self._get_request_body(WebSocketMessageTypeEnum.ADD_JOB, request_data)
        self._send_json(request_body)

    def get_group_list(self):
        ''' 群列表
        '''
        job_data = {}
        request_data = self._get_add_job_request_data(
            PackageNameEnum.WECHAT,
            JobNameEnum.GET_GROUP_LIST,
            job_data
        )
        request_body = self._get_request_body(WebSocketMessageTypeEnum.ADD_JOB, request_data)
        self._send_json(request_body)

    def send_image(self, wxid, image_path):
        ''' 发图片消息
        '''
        job_data = {
            'wxid': wxid,
            'image_path': image_path
        }
        request_data = self._get_add_job_request_data(
            PackageNameEnum.WECHAT,
            JobNameEnum.SEND_IMAGE,
            job_data
        )
        request_body = self._get_request_body(WebSocketMessageTypeEnum.ADD_JOB, request_data)
        self._send_json(request_body)

    def send_text_message(self, wxid, content, at_string):
        job_data = {
            'wxid': wxid,
            'content': content,
            'at_string': at_string
        }
        request_data = self._get_add_job_request_data(
            PackageNameEnum.WECHAT,
            JobNameEnum.SEND_TEXT_MESSAGE,
            job_data
        )
        request_body = self._get_request_body(WebSocketMessageTypeEnum.ADD_JOB, request_data)
        self._send_json(request_body)

    def send_muti_text(self, wxids, content):
        job_data = {
            'wxids': wxids,
            'content': content
        }
        request_data = self._get_add_job_request_data(
            PackageNameEnum.WECHAT,
            JobNameEnum.SEND_MUTI_TEXT,
            job_data
        )
        request_body = self._get_request_body(WebSocketMessageTypeEnum.ADD_JOB, request_data)
        self._send_json(request_body)
    
    def send_muti_image(self, wxids, image_path, is_gif):
        job_data = {
            'wxids': wxids,
            'image_path': image_path,
            'is_gif': is_gif
        }
        request_data = self._get_add_job_request_data(
            PackageNameEnum.WECHAT,
            JobNameEnum.SEND_MUTI_IMAGE,
            job_data
        )
        request_body = self._get_request_body(WebSocketMessageTypeEnum.ADD_JOB, request_data)
        self._send_json(request_body)

    def retransmit_msg(self, wxids, msg_server_id):
        ''' 转发
        '''
        job_data = {
            'wxids': wxids,
            'field_msgSvrId': str(msg_server_id)
        }
        request_data = self._get_add_job_request_data(
            PackageNameEnum.WECHAT,
            JobNameEnum.RETRANSMIT_MSG,
            job_data
        )
        request_body = self._get_request_body(WebSocketMessageTypeEnum.ADD_JOB, request_data)
        self._send_json(request_body)

    def cancel_job(self, cancel_job_id):
        ''' 取消任务
        '''
        job_data = {
            'cancel_job_id': cancel_job_id
        }
        request_data = self._get_add_job_request_data(
            PackageNameEnum.WECHAT,
            JobNameEnum.CANCEL_JOB,
            job_data
        )
        request_body = self._get_request_body(WebSocketMessageTypeEnum.ADD_JOB, request_data)
        self._send_json(request_body)


class JobResultHandler():
    def __init__(self, device_id, params):
        logger.info('[job_result] receive message from {}: {}'.format(device_id, params))
        self.device_id = device_id
        self.params = params
        self.handler_map = {
            JobNameEnum.GET_LOCAL_USER_INFO: self.get_local_user_info,
            JobNameEnum.GET_USER_LIST: self.get_user_list,
            JobNameEnum.GET_GROUP_LIST: self.get_group_list
        }

    def handle(self):
        self.job_id = self.params.get('job_id')
        job_name = self.params.get('job_name')
        job_status = self.params.get('job_status')
        if job_status == JobStatusEnum.FINISH:
            if job_name not in self.handler_map:
                return
            func = self.handler_map.get(job_name)
            result_data = json.loads(self.params.get('result_data'))
            func(result_data)
        elif job_status == JobStatusEnum.FAIL:
            t = threading.Thread(target=self.fail_result_handler)
            t.start()
            # self.fail_result_handler()

    def get_local_user_info(self, result_data):
        ''' 暂时没有业务场景, 暂不做缓存处理
        '''
        user = result_data.get('user')
        pass

    def get_user_list(self, result_data):
        users = result_data.get('users')
        friend_wxids = set()
        for user in users:
            remark = user.get('field_conRemark')
            if not remark.startswith('自转'):
                continue
            friend_wxid = user.get('field_username')
            if friend_wxid:
                friend_wxids.add(friend_wxid)
        DEVICE_FRIENDS_MAP[self.device_id] = friend_wxids

    def get_group_list(self, result_data):
        groups = result_data.get('groups')
        group_wxids = set()
        for group in groups:
            member_count = group.get('field_memberCount')
            if member_count < 5:
                continue
            group_wxid = group.get('field_chatroomname')
            if group_wxid:
                group_wxids.add(group_wxid)
        DEVICE_GROUPS_MAP[self.device_id] = group_wxids

    def fail_result_handler(self):
        time.sleep(3)
        ws_handler = DEVICE_WEBSOCKET_HANDLER_MAP.get(self.device_id)
        if ws_handler:
            ws_handler.cancel_job(self.job_id)


class EventHandler():
    def __init__(self, device_id, params):
        logger.info('[event] receive message from {}: {}'.format(device_id, params))
        self.device_id = device_id
        self.params = params
        self.handler_map = {
            EventNameEnum.CHAT_MESSAGE: self.get_chat_message
        }

    def handle(self):
        event_name = self.params.get('event_name')
        event_data = self.params.get('event_data')
        if event_name not in self.handler_map:
            return
        func = self.handler_map[event_name]
        func(event_data)

    def get_chat_message(self, event_data):
        message = event_data
        msg_server_id = message.get('field_msgSvrId')
        is_sender = message.get('field_isSend')
        if is_sender:
            return
        talker_wxid = message.get('field_talker')
        friend_wxids = DEVICE_FRIENDS_MAP.get(self.device_id, set())
        if talker_wxid not in friend_wxids:
            return
        content = message.get('content')
        content_type = content.get('type')
        is_group = content.get('is_group')
        image_origin = content.get('image_origin')
        if is_group:
            return
        if content_type not in ALLOWED_RETRANSMIT_MESSAGE_TYPES:
            return
        if content_type == WeChatMessageContentTypeEnum.IMAGE and image_origin != 1:
            # 图片消息若不是大图不转发
            return
        group_wxids = DEVICE_GROUPS_MAP.get(self.device_id)
        if not group_wxids:
            return
        group_wxids_string = ','.join(group_wxids)
        ws_handler = DEVICE_WEBSOCKET_HANDLER_MAP.get(self.device_id)
        if not ws_handler:
            return
        ws_handler.retransmit_msg(group_wxids_string, msg_server_id)


class PushMessageHandler():
    def __init__(self, params):
        self.params = params

    def handle(self):
        message_type = self.params['message_type']
        message = self.params['message']
        is_gif = self.params.get('is_gif')
        if not message:
            return
        for device_id, ws_handler in DEVICE_WEBSOCKET_HANDLER_MAP.items():
            group_wxids = DEVICE_GROUPS_MAP.get(device_id, set())
            if not group_wxids:
                continue
            group_wxids_string = ','.join(group_wxids)
            if message_type == PushMessageType.IMAGE:
                ws_handler.send_muti_image(group_wxids_string, message, is_gif)
            elif message_type == PushMessageType.TEXT:
                ws_handler.send_muti_text(group_wxids_string, message)
