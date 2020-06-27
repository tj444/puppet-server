import json
import time
import traceback
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from common.utils import success_response, failed_response
from .handler import JobResultHandler, EventHandler, PushMessageHandler
from common.enums import PushMessageType, ImageIsGIF


logger = logging.getLogger('django')


@require_POST
def event(request):
    device_id = request.headers.get('deviceid')
    if not device_id:
        errmsg = '缺少deviceid'
        return JsonResponse(failed_response(errmsg))
    params = json.loads(request.body)
    try:
        handler = EventHandler(device_id, params)
        handler.handle()
    except Exception as e:
        logger.info(traceback.format_exc())
        return JsonResponse(failed_response())
    return JsonResponse(success_response())


@require_POST
def job_callback(request):
    device_id = request.headers.get('deviceid')
    if not device_id:
        errmsg = '缺少deviceid'
        return JsonResponse(failed_response(errmsg))
    params = json.loads(request.body)
    try:
        handler = JobResultHandler(device_id, params)
        handler.handle()
    except Exception as e:
        logger.info(traceback.format_exc())
        return JsonResponse(failed_response())
    return JsonResponse(success_response())


@require_POST
def push_message(request):
    params = json.loads(request.body)
    biz_type = params.get('biz_type')
    if biz_type not in settings.ALLOWED_PUSH_MESSAGE_CONFIG:
        errmsg = '该业务暂不允许推送'
        return JsonResponse(failed_response(errmsg))
    now = time.strftime('%H:%M', time.localtime(time.time()))
    allowed_time_list = settings.ALLOWED_PUSH_MESSAGE_CONFIG[biz_type]
    is_allowed = False
    for allowed_time in allowed_time_list:
        if now >= allowed_time[0] and now < allowed_time[1]:
            is_allowed = True
            break
    if not is_allowed:
        errmsg = '该时间段暂不允许推送'
        return JsonResponse(failed_response(errmsg))
    data = params.get('data')
    for item in data:
        message_type = item.get('message_type')
        if message_type not in PushMessageType.get_keys():
            continue
        is_gif = item.get('is_gif')
        if message_type == PushMessageType.IMAGE and is_gif not in ImageIsGIF.get_keys():
            continue
        try:
            handler = PushMessageHandler(item)
            handler.handle()
        except Exception as ex:
            logger.info(traceback.format_exc())
    return JsonResponse(success_response())

