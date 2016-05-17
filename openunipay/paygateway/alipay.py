from . import PayGateway
from django.db import transaction
from ..ali_pay.models import AliPayOrder
from ..ali_pay import ali_pay_lib

class AliPayGateway(PayGateway):
    
    @transaction.atomic
    def create_order(self, orderItemObj, clientIp):
        aliOrderObj = AliPayOrder()
        aliOrderObj.out_trade_no = orderItemObj.orderno
        aliOrderObj.subject = orderItemObj.product_desc
        aliOrderObj.body = orderItemObj.product_detail
        aliOrderObj.total_fee = orderItemObj.fee / 100
        aliOrderObj.it_b_pay = '30m'
        aliOrderObj.sign()
        aliOrderObj.save()
        ali_pay_lib.create_order(aliOrderObj)
        return aliOrderObj.interface_data
    
    @transaction.atomic
    def process_notify(self, requestContent):
        return ali_pay_lib.process_notify(requestContent)

    @transaction.atomic
    def query_order(self, orderNo):
        return ali_pay_lib.query_order(orderNo)
