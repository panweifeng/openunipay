import logging
from django.http import HttpResponse
from openunipay.models import PAY_WAY_WEIXIN
from openunipay.paygateway import unipay

_logger = logging.getLogger('weixin_pay_notificaiton')

def process_notify(request):
    _logger.info('received weixin pay notification.body:{}'.format(request.body))
    unipay.process_notify(PAY_WAY_WEIXIN, request.body)
    return HttpResponse('<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>',
                        'application/xml', 200)
