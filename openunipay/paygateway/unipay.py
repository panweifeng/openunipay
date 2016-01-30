from django.db import transaction
from openunipay.models import OrderItem, PAY_WAY_WEIXIN, PAY_WAY_ALI
from openunipay.paygateway import weixin, alipay
from openunipay import exceptions
from openunipay.util import datetime
    
_PAY_GATEWAY = {PAY_WAY_WEIXIN:weixin.WeiXinPayGateway(),
                PAY_WAY_ALI:alipay.AliPayGateway(), }

@transaction.atomic
def create_order(orderno, payway, clientIp, product_desc, product_detail, fee, user=None, attach=None, expire=1440):
    '''
    @summary: create order
    @param orderno: order no
    @param payway: payway
    @param expire: expire in minutes 
    '''
    if not is_supportted_payway(payway):
        raise exceptions.PayWayError()
    
    orderItemObj = OrderItem()
    orderItemObj.orderno = orderno
    orderItemObj.user = user
    orderItemObj.product_desc = product_desc
    orderItemObj.product_detail = product_detail
    orderItemObj.fee = fee
    orderItemObj.payway = payway
    orderItemObj.attach = attach
    orderItemObj.initial_orlder(expire)
    orderItemObj.save()
    
    # send order to pay gateway
    gatewayData = _PAY_GATEWAY[payway].create_order(orderItemObj, clientIp)
    return gatewayData

@transaction.atomic
def query_order(orderno):
    orderItemObj = OrderItem.objects.get(orderno=orderno)
    payResult = _PAY_GATEWAY[orderItemObj.payway].query_order(orderItemObj.orderno)
    if payResult.Succ:
        orderItemObj.paied = True
        orderItemObj.dt_pay = datetime.local_now()
        orderItemObj.save()
    return payResult

@transaction.atomic
def process_notify(payway, requestContent):
    if not is_supportted_payway(payway):
        raise exceptions.PayWayError()
    payResult = _PAY_GATEWAY[payway].process_notify(requestContent)
    if payResult.Succ:
        orderItemObj = OrderItem.objects.get(orderno=payResult.OrderNo)
        orderItemObj.paied = True
        orderItemObj.dt_pay = datetime.local_now()
        orderItemObj.save()
    return payResult

def is_supportted_payway(payway):
    return payway in _PAY_GATEWAY
