import os
import time
import logging
import traceback
import requests
from django.conf import settings
from common.enums import PushMessageType


logger = logging.getLogger('crontab')


def push_message():
    ''' 扫描tasks文件, 每一行是一个任务, 
    '''
    api = settings.HOST_URL + '/push_message'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, 'tasks')
    items = []
    now = time.strftime('%H:%M', time.localtime(time.time()))
    with open(filepath) as fp:
        for line in fp:
            data = line.strip().split('|')
            if len(data) >= 3:
                run_at = data[0]
                if now != run_at:
                    continue
                message_type = data[1]
                message = data[2]
                is_gif = None
                if len(data) > 3:
                    is_gif = int(data[3])
                if message_type not in PushMessageType.get_keys():
                    continue
                item = {
                    'message_type': message_type,
                    'message': message,
                    'is_gif': is_gif
                }
                items.append(item)
    if not items:
        return
    logger.info('cron push_message start')
    try:
        params = {
            'biz_type': 'crontab',
            'data': items
        }
        logger.info(params)
        requests.post(api, json=params)
    except Exception as ex:
        logger.info(traceback.format_exc())
    logger.info('cron push_message finish')


if __name__ == '__main__':
    push_message()
