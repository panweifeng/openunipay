# -*- coding: utf-8 -*-
from django.db import models
from openunipay.util import random_helper
from .security import sign
from . import xml_helper


_ORDER_NONCE_POPULATION = '123457890ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class WeiXinOrder(models.Model):
    appid = models.CharField(verbose_name=u'公众账号ID', max_length=32, editable=False)
    mch_id = models.CharField(verbose_name=u'商户号', max_length=32, editable=False)
    body = models.CharField(verbose_name=u'商品描述', max_length=128, editable=False)
    attach = models.CharField(verbose_name=u'附加数据', max_length=127, null=True, blank=True, editable=False)
    out_trade_no = models.CharField(verbose_name=u'商户订单号', max_length=32, db_index=True, editable=False)
    fee_type = models.CharField(verbose_name=u'货币类型', max_length=16, editable=False)
    total_fee = models.SmallIntegerField(verbose_name=u'总金额', editable=False)
    spbill_create_ip = models.CharField(verbose_name=u'终端IP', max_length=16, editable=False)
    time_start = models.CharField(verbose_name=u'交易起始时间', max_length=14, editable=False)
    time_expire = models.CharField(verbose_name=u'交易结束时间', max_length=14, editable=False)
    notify_url = models.CharField(verbose_name=u'通知地址', max_length=256, editable=False)
    trade_type = models.CharField(verbose_name=u'交易类型', max_length=16, editable=False)
    
    class Meta:
        verbose_name = u'微信统一订单'
        verbose_name_plural = u'微信统一订单'
        
    def __str__(self):
        return self.out_trade_no
        
    def _get_vlaue_dict(self):
        fieldsList = WeiXinOrder._meta.get_fields()
        return {item.attname:getattr(self, item.attname) 
                for item in fieldsList 
                if not item.auto_created and getattr(self, item.attname)}
    
    def to_xml(self):
        # sign data
        valueDict = self._get_vlaue_dict()
        valueDict['nonce_str'] = random_helper.generate_nonce_str(23)
        valueDict['sign'] = sign(valueDict)
        return xml_helper.dict_to_xml(valueDict)

class WeiXinPayResult(models.Model):
    order = models.OneToOneField(WeiXinOrder,
                                 on_delete=models.CASCADE,
                                 primary_key=True,
                                 editable=False,
                                 related_name='pay_result')
    prepayid = models.CharField(verbose_name=u'预支付交易会话标识', null=True, blank=True, max_length=64, db_index=True, editable=False)
    openid = models.CharField(verbose_name=u'用户标识(openId)', null=True, blank=True, max_length=128, editable=False)
    bank_type = models.CharField(verbose_name=u'付款银行', null=True, blank=True, max_length=16, editable=False)
    total_fee = models.SmallIntegerField(verbose_name=u'总金额', null=True, blank=True, editable=False)
    attach = models.CharField(verbose_name=u'商户附加数据', null=True, blank=True, max_length=128, editable=False)
    tradestate = models.CharField(verbose_name=u'交易状态', null=True, blank=True, max_length=32, editable=False)
    tradestatedesc = models.CharField(verbose_name=u'交易状态描述', null=True, blank=True, max_length=256, editable=False)
    
    
    def __str__(self):
        fieldsList = WeiXinPayResult._meta.get_fields()
        temp = []
        for field in fieldsList:
            if not field.auto_created:
                temp.append('{}:{}'.format(field.verbose_name, getattr(self, field.attname)))
        return ','.join(temp) 
        
            
        
