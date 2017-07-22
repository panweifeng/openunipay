from . import PayGateway
from django.db import transaction
from django.conf import settings
from openunipay.util import random_helper, datetime
from openunipay.weixin_pay.models import WeiXinOrder, WeiXinQRPayEntity
from openunipay.weixin_pay import weixin_pay_lib, security, xml_helper
from openunipay.models import OrderItem, Product, PAY_WAY_WEIXIN


class WeiXinPayGateway(PayGateway):
    @transaction.atomic
    def create_order(self, orderItemObj, clientIp, **kwargs):
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
        weixinOrderObj.trade_type = kwargs.get('trade_type', 'APP')
        weixinOrderObj.openid = kwargs.get('openid')
        weixinOrderObj.save()
        prepayid = weixin_pay_lib.create_order(weixinOrderObj)
        data = {'appid': settings.WEIXIN['app_id'],
                'partnerid': settings.WEIXIN['mch_id'],
                'prepayid': prepayid,
                'package': 'Sign=WXPay',
                'noncestr': random_helper.generate_nonce_str(23),
                'timestamp': str(datetime.get_unix_timestamp())}
        data['sign'] = security.sign(data)
        return data

    @transaction.atomic
    def process_notify(self, requestContent):
        return weixin_pay_lib.process_notify(requestContent)

    @transaction.atomic
    def query_order(self, orderNo):
        return weixin_pay_lib.query_order(orderNo)

    @transaction.atomic
    def generate_qr_pay_url(self, product_id):
        qrPayEntiry = WeiXinQRPayEntity()
        qrPayEntiry.appid = settings.WEIXIN['app_id']
        qrPayEntiry.mch_id = settings.WEIXIN['mch_id']
        qrPayEntiry.time_stamp = str(datetime.get_unix_timestamp())
        qrPayEntiry.product_id = product_id
        qrPayEntiry.save()
        url = weixin_pay_lib.request_shorten_url(qrPayEntiry.to_raw_rul())
        return url

    @transaction.atomic
    def process_qr_pay_notify(self, requestContent):
        notifyObj = weixin_pay_lib.process_qr_pay_notify(requestContent)

        productObj = Product.objects.get(productid=notifyObj['product_id'])

        orderItemObj = OrderItem()
        orderItemObj.orderno = self._generate_qr_orderno(productObj.productid)
        orderItemObj.user = notifyObj['openid']
        orderItemObj.product_desc = productObj.product_desc
        orderItemObj.product_detail = productObj.product_detail
        orderItemObj.fee = productObj.fee
        orderItemObj.payway = PAY_WAY_WEIXIN
        orderItemObj.attach = None
        orderItemObj.initial_orlder(1440)
        orderItemObj.save()

        weixinOrderItem = self.create_order(orderItemObj, settings.WEIXIN['clientIp'], trade_type='NATIVE', openid=notifyObj['openid'])

        data = {
            'return_code': 'SUCCESS',
            'result_code': 'SUCCESS',
            'appid': settings.WEIXIN['app_id'],
            'mch_id': settings.WEIXIN['mch_id'],
            'prepay_id': weixinOrderItem['prepayid'],
            'nonce_str': notifyObj['nonce_str'],
        }
        data['sign'] = security.sign(data)
        return xml_helper.dict_to_xml(data)

    def _generate_qr_orderno(self, productid):
        return 'WXQR-{}-{}'.format(productid, datetime.get_unix_timestamp())
