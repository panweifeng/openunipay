# -*- coding: utf-8 -*-
import requests
import logging
from .exceptions import APIError
from .models import WeiXinOrder, WeiXinPayResult
from .security import sign
from . import xml_helper
from openunipay.util import random_helper
from openunipay.paygateway import PayResult
from openunipay import exceptions

CODE_SUCC = 'SUCCESS'
TRADE_STATE_SUCC = ('SUCCESS',)
TRADE_STATE_LAPSED = ('CLOSED', 'REVOKED')
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
    try:
        responseData = xml_helper.xml_to_dict(notifyContent) 
        result = _process_order_result(responseData)
        return result
    except:
        _logger.exception('process pay result notification failed. received:{}'.format(notifyContent))

def query_order(orderNo):
    weixinOrderObj = WeiXinOrder.objects.get(out_trade_no=orderNo)
    
    result = _compose_pay_result(orderNo, weixinOrderObj.pay_result.tradestate)
    if result.Succ or result.Lapsed:
        return result
    
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
    if r.status_code == 200:
        responseData = xml_helper.xml_to_dict(r.text)
        result = _process_order_result(responseData)
        return result
    else:
        raise exceptions.PayProcessError('request processed failed. body:{}'.format(r.content))       

def _process_order_result(responseData):
    if responseData['return_code'] == CODE_SUCC:
        if responseData['result_code'] == CODE_SUCC:
            # check sign
            signStr = responseData['sign']
            del responseData['sign']
            signCheck = sign(responseData)
            if signStr != signCheck:
                _logger.error('received untrusted pay notification:{}'.format(responseData))
                raise exceptions.InsecureDataError()
            else:
                # save data
                weixinOrderObj = WeiXinOrder.objects.get(out_trade_no=responseData['out_trade_no'])
                payResultObj = weixinOrderObj.pay_result
                payResultObj.openid = responseData.get('openid')
                payResultObj.bank_type = responseData.get('bank_type')
                payResultObj.total_fee = responseData.get('total_fee')
                payResultObj.attach = responseData.get('attach')
                payResultObj.tradestate = responseData.get('trade_state', 'SUCCESS')
                payResultObj.tradestatedesc = responseData.get('trade_state_desc')
                payResultObj.save()
                result = _compose_pay_result(responseData['out_trade_no'], payResultObj.tradestate)
                return result
        else:
            raise exceptions.PayProcessError('trade processed failed. err_code:{},err_code_desc:{}'.format(responseData.get('err_code'), responseData.get('err_code_des')))
            _logger.error('trade processed failed. response:{}'.format(responseData))
    else:
        raise exceptions.PayProcessError('request processed failed. return_msg:{}'.format(responseData.get('return_msg')))
        _logger.error('data communication failed. response:{}'.format(responseData))
    
def _format_log_message(message, r):
    return u'''
           {}
           url:{}
           response code:{}
           response body:{}
           '''.format(message, r.url, r.status_code, r.text)
           
def _compose_pay_result(orderNo, tradestate):
    result = PayResult(orderNo)
    result.succ = tradestate in TRADE_STATE_SUCC
    result.lapsed = tradestate in TRADE_STATE_LAPSED
    return result
