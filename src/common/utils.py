import time
import random
from common.enums import ResponseStatusEnum


def generate_request_id():
    ''' 请求唯一标识, 毫秒时间戳+3位随机数, 共16位数字
    '''
    return int(str(int(time.time() * 1000)) + str(random.randint(0, 999)).rjust(3, '0'))


def generate_job_id():
    ''' 先和request_id保持一致的逻辑, 后续有需要可以改生成逻辑
    '''
    return generate_request_id()


def success_response(data=None):
    ret = {
        'status': ResponseStatusEnum.SUCCESS_STATUS,
        'message': 'success'
    }
    if data:
        ret['data'] = data
    return ret


def failed_response(err_message=None):
    return {
        'status': ResponseStatusEnum.FAILED_STATUS,
        'message': err_message or 'failed'
    }

