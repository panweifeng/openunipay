# -*- coding: utf-8 -*-
from .models import AliPayOrder, AliPayResult
from .security import verify
from openunipay.paygateway import PayResult
from openunipay.ali_pay import logger

TRADE_STATE_SUCC = 'TRADE_FINISHED'

def create_order(orderObj):
    assert isinstance(orderObj, AliPayOrder)
    AliPayResult.objects.create(order=orderObj)
    
def process_notify(request):
    result = PayResult(False, None)
    try:
        _process_order_result(dict(request.POST), result)
    except:
        logger.exception('process pay result notification failed. received:{}'.format(request.body))
    return result

def query_order(orderNo):
    orderObj = AliPayOrder.objects.get(out_trade_no=orderNo)
    result = PayResult(False, None)
    result.succ = orderObj.pay_result.trade_status == TRADE_STATE_SUCC
    result.orderno = orderObj.out_trade_no
    return result       

def _process_order_result(valueDict, result):
    if verify(valueDict):
        # save data
        orderObj = AliPayOrder.objects.get(out_trade_no=valueDict['out_trade_no'])
        payResultObj = orderObj.pay_result
        payResultObj.out_trade_no = valueDict.get('out_trade_no')
        payResultObj.notify_time = valueDict.get('notify_time')
        payResultObj.notify_type = valueDict.get('notify_type')
        payResultObj.notify_id = valueDict.get('notify_id')
        payResultObj.subject = valueDict.get('subject')
        payResultObj.trade_no = valueDict.get('trade_no')
        payResultObj.trade_status = valueDict.get('trade_status')
        payResultObj.seller_id = valueDict.get('seller_id')
        payResultObj.seller_email = valueDict.get('seller_email')
        payResultObj.buyer_id = valueDict.get('buyer_id')
        payResultObj.buyer_email = valueDict.get('buyer_email')
        payResultObj.total_fee = valueDict.get('total_fee')
        payResultObj.save()
    else:
        logger.error('received unverified notification:{}'.format(valueDict))
    
