# -*- coding: utf-8 -*-
from .models import AliPayOrder, AliPayResult
from openunipay.paygateway import PayResult
from openunipay.ali_pay import logger, security
from openunipay import exceptions

TRADE_STATUS_SUCC = ('TRADE_SUCCESS', 'TRADE_FINISHED',)
TRADE_STATUS_LAPSED = ('TRADE_CLOSED',)

def create_order(orderObj):
    assert isinstance(orderObj, AliPayOrder)
    AliPayResult.objects.create(order=orderObj)
    
def process_notify(request):
    valueDict = request.POST.dict()
    if security.verify_ali_data(valueDict):
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
        result = _compose_pay_result(payResultObj.out_trade_no, payResultObj.trade_status)
        return result     
    else:
        logger.error('received unverified notification:{}'.format(valueDict))
        raise exceptions.InsecureDataError()

def query_order(orderNo):
    orderObj = AliPayOrder.objects.get(out_trade_no=orderNo)
    result = _compose_pay_result(orderObj.out_trade_no, orderObj.pay_result.trade_status)
    return result 

def _compose_pay_result(orderNo, trade_status):
    result = PayResult(orderNo)
    result.succ = trade_status in TRADE_STATUS_SUCC
    result.lapsed = trade_status in TRADE_STATUS_LAPSED
    return result      
