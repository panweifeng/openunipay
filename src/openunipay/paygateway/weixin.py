from . import PayGateway
from django.db import transaction
from django.conf import settings
from openunipay.util import random_helper,datetime
from openunipay.weixin_pay.models import WeiXinOrder
from openunipay.weixin_pay import weixin_pay_lib, security

class WeiXinPayGateway(PayGateway):
    
    @transaction.atomic
    def create_order(self, orderItemObj, clientIp):
        weixinOrderObj = WeiXinOrder()
        weixinOrderObj.appid = settings.WEIXIN['app_id']
        weixinOrderObj.mch_id = settings.WEIXIN['mch_id']
        weixinOrderObj.body = orderItemObj.product_desc
        weixinOrderObj.attach = orderItemObj.attach
        weixinOrderObj.out_trade_no = orderItemObj.orderno
        weixinOrderObj.total_fee = orderItemObj.fee
        weixinOrderObj.spbill_create_ip = clientIp
        weixinOrderObj.time_start = orderItemObj.dt_start.strftime("%Y%m%d%H%M%S")
        weixinOrderObj.time_expire = orderItemObj.dt_end.strftime("%Y%m%d%H%M%S")
        weixinOrderObj.notify_url = settings.WEIXIN['mch_notify_url']
        weixinOrderObj.trade_type = 'APP'
        weixinOrderObj.save()
        prepayid = weixin_pay_lib.create_order(weixinOrderObj)
        data = {'appid':settings.WEIXIN['app_id'],
                'partnerid':settings.WEIXIN['mch_id'],
                'prepayid':prepayid,
                'package':'Sign=WXPay',
                'noncestr':random_helper.generate_nonce_str(23),
                'timestamp':str(datetime.get_unix_timestamp())}
        data['sign'] = security.sign(data)
        return data
    
    @transaction.atomic
    def process_notify(self, requestContent):
        return weixin_pay_lib.process_notify(requestContent)

    @transaction.atomic
    def query_order(self, orderNo):
        return weixin_pay_lib.query_order(orderNo)
