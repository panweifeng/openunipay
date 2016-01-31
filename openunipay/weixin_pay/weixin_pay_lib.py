# -*- coding: utf-8 -*-
import requests
import logging
from .exceptions import APIError
from .models import WeiXinOrder, WeiXinPayResult
from .security import sign
from . import xml_helper
from openunipay.util import random_helper
from openunipay.paygateway import PayResult

CODE_SUCC = 'SUCCESS'
TRADE_STATE_SUCC = 'SUCCESS'
_logger = logging.getLogger('openunipay.weixin')

def create_order(weixinOrderObj):
    assert isinstance(weixinOrderObj, WeiXinOrder)
    payResultObj = WeiXinPayResult.objects.create(order=weixinOrderObj)
    url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    data = weixinOrderObj.to_xml().encode()
    r = requests.post(url, data=data, headers={'Content-Type':'application/xml'}, verify=False)
    r.encoding = 'utf-8'
    if r.status_code == 200:
        responseData = xml_helper.xml_to_dict(r.text)
        if responseData['return_code'] == CODE_SUCC and responseData['result_code'] == CODE_SUCC:
            payResultObj.prepayid = responseData['prepay_id']
            payResultObj.save()
            return responseData['prepay_id']
        else:
            _logger.error(_format_log_message('create_order failed', r))
            raise APIError(responseData['return_msg'])
    else:
        _logger.error(_format_log_message('create_order failed', r))
        raise APIError()
    
def process_notify(notifyContent):
    result = PayResult(False, None)
    try:
        responseData = xml_helper.xml_to_dict(notifyContent) 
        _process_order_result(responseData, result)
    except:
        _logger.exception('process pay result notification failed. received:{}'.format(notifyContent))
    return result

def query_order(orderNo):
    weixinOrderObj = WeiXinOrder.objects.get(out_trade_no=orderNo)
    url = 'https://api.mch.weixin.qq.com/pay/orderquery'
    valueDict = {
          'appid':weixinOrderObj.appid,
          'mch_id':weixinOrderObj.mch_id,
          'out_trade_no':weixinOrderObj.out_trade_no,
          'nonce_str':random_helper.generate_nonce_str(23)
          }
    valueDict['sign'] = sign(valueDict)
    data = xml_helper.dict_to_xml(valueDict)
    r = requests.post(url, data=data, headers={'Content-Type':'application/xml'}, verify=False)
    r.encoding = 'utf-8'
    result = PayResult(False, None)
    if r.status_code == 200:
        responseData = xml_helper.xml_to_dict(r.text)
        _process_order_result(responseData, result)
    return result       

def _process_order_result(responseData, result):
    if responseData['return_code'] == CODE_SUCC and responseData['result_code'] == CODE_SUCC:
        # check sign
        signStr = responseData['sign']
        del responseData['sign']
        signCheck = sign(responseData)
        if signStr != signCheck:
            _logger.error('received untrusted pay notification:{}'.format(responseData))
        else:
            # save data
            weixinOrderObj = WeiXinOrder.objects.get(out_trade_no=responseData['out_trade_no'])
            payResultObj = weixinOrderObj.pay_result
            payResultObj.openid = responseData.get('openid')
            payResultObj.bank_type = responseData.get('bank_type')
            payResultObj.total_fee = responseData.get('total_fee')
            payResultObj.attach = responseData.get('attach')
            payResultObj.tradestate = responseData.get('trade_state')
            payResultObj.tradestatedesc = responseData.get('trade_state_desc')
            payResultObj.save()
            result.succ = payResultObj.tradestate == TRADE_STATE_SUCC
            result.orderno = responseData['out_trade_no']
    else:
        _logger.error('received pay failed notification:{}'.format(responseData))
    
def _format_log_message(message, r):
    return u'''
           {}
           url:{}
           response code:{}
           response body:{}
           '''.format(message, r.url, r.status_code, r.text)
