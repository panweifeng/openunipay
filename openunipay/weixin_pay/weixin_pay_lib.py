# -*- coding: utf-8 -*-
import requests
import logging
from urllib import parse
from django.conf import settings
from openunipay.weixin_pay.exceptions import APIError
from openunipay.weixin_pay.models import WeiXinOrder, WeiXinPayResult, WeiXinQRPayRecord
from openunipay.weixin_pay.security import sign
from openunipay.weixin_pay import xml_helper
from openunipay.util import random_helper
from openunipay.paygateway import PayResult
from openunipay import exceptions

CODE_SUCC = 'SUCCESS'
TRADE_STATE_SUCC = ('SUCCESS', )
TRADE_STATE_LAPSED = ('CLOSED', 'REVOKED')

_logger = logging.getLogger('openunipay.weixin')


############### 统一下单 #######################
def create_order(weixinOrderObj):
    assert isinstance(weixinOrderObj, WeiXinOrder)
    _logger.info("creating order")
    payResultObj = WeiXinPayResult.objects.create(order=weixinOrderObj)
    url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    data = weixinOrderObj.to_xml().encode()
    _logger.info("request data is:{}".format(data))
    r = requests.post(url, data=data, headers={'Content-Type': 'application/xml'}, verify=False)

    def handle_response(responseData):
        payResultObj.prepayid = responseData['prepay_id']
        payResultObj.save()
        _logger.info("order created. prepayid is {}".format(payResultObj.prepayid))
        return responseData['prepay_id']

    return __handle_weixin_api_xml_response(r, handle_response)


############# 处理微信支付 异步通知 #############
def process_notify(notifyContent):
    responseData = xml_helper.xml_to_dict(notifyContent)
    # check sign
    if responseData['return_code'] == CODE_SUCC:
        __verify_response_data(responseData)
        result = _process_order_result(responseData)
        return result
    else:
        return None


def query_order(orderNo):
    weixinOrderObj = WeiXinOrder.objects.get(out_trade_no=orderNo)

    result = _compose_pay_result(orderNo, weixinOrderObj.pay_result.tradestate)
    if result.Succ or result.Lapsed:
        return result

    valueDict = {'appid': weixinOrderObj.appid, 'mch_id': weixinOrderObj.mch_id, 'out_trade_no': weixinOrderObj.out_trade_no, 'nonce_str': random_helper.generate_nonce_str(23)}
    valueDict['sign'] = sign(valueDict)
    data = xml_helper.dict_to_xml(valueDict)

    url = 'https://api.mch.weixin.qq.com/pay/orderquery'
    r = requests.post(url, data=data, headers={'Content-Type': 'application/xml'}, verify=False)

    return __handle_weixin_api_xml_response(r, _process_order_result)


def _process_order_result(responseData):
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


def _compose_pay_result(orderNo, tradestate):
    result = PayResult(orderNo)
    result.succ = tradestate in TRADE_STATE_SUCC
    result.lapsed = tradestate in TRADE_STATE_LAPSED
    return result


############ 扫码支付 ##################
def process_qr_pay_notify(notifyContent):
    '''
    @summary: 处理微信扫码支付异步通知
    '''
    responseData = xml_helper.xml_to_dict(notifyContent)
    # check sign
    __verify_response_data(responseData)
    # process data
    qrPayRecord = WeiXinQRPayRecord.objects.create(
        appid=responseData.get('appid'), mch_id=responseData.get('mch_id'), openid=responseData.get('openid'), product_id=responseData.get('product_id'))
    return {'product_id': qrPayRecord.product_id, 'openid': qrPayRecord.openid, 'nonce_str': responseData.get('nonce_str')}


############ 转换短连接 ##################
def request_shorten_url(url):
    _logger.info("get shorten url")
    data = {
        'appid': settings.WEIXIN['app_id'],
        'mch_id': settings.WEIXIN['mch_id'],
        'long_url': url,
        'nonce_str': random_helper.generate_nonce_str(23),
    }
    data['sign'] = sign(data)
    requestBody = xml_helper.dict_to_xml(data)
    _logger.info("request data is:{}".format(requestBody))

    url = 'https://api.mch.weixin.qq.com/tools/shorturl'
    r = requests.post(url, data=requestBody, headers={'Content-Type': 'application/xml'}, verify=False)
    return __handle_weixin_api_xml_response(r, lambda responseData: responseData['short_url'])


########
def __verify_response_data(responseData):
    '''
    @summary: 使用签名验证微信服务器的返回数据
    @param responseData:返回数据的Dict,里面需包含sign字段. 验证成功后sign字段会被删除
    @return 如果验证失败会抛出异常
    '''
    signStr = responseData['sign']
    del responseData['sign']
    signCheck = sign(responseData)
    if signStr != signCheck:
        _logger.error('received untrusted data')
        raise exceptions.InsecureDataError()


def __handle_weixin_api_xml_response(r, func):
    '''
    @summary: 处理微信API返回结果
    @param func:数据处理function, 会在请求成功并且验证成功的时候调用
    @return 如果验证失败会抛出异常
    '''
    r.encoding = 'utf-8'
    _logger.info("response body is:{}".format(r.text))
    if r.status_code == 200:
        responseData = xml_helper.xml_to_dict(r.text)
        if responseData['return_code'] == CODE_SUCC:
            # check sign
            __verify_response_data(responseData)
            if responseData['result_code'] == CODE_SUCC:
                return func(responseData)
            else:
                raise APIError(responseData['err_code'])
        else:
            raise APIError('data sign verfied failed')
    else:
        raise APIError('status from weixin is not 200')
