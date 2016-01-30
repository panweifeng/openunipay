import logging
from django.http import HttpResponse
from openunipay.models import PAY_WAY_ALI
from openunipay.paygateway import unipay

_logger = logging.getLogger('openunipay_ali_pay_notificaiton')

def process_notify(request):
    _logger.info('received ali pay notification.body:{}'.format(request.body))
    unipay.process_notify(PAY_WAY_ALI, request)
    return HttpResponse('success', 'text/plain-text', 200)
