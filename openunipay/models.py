# -*- coding: utf-8 -*-

from django.db import models
from openunipay.ali_pay.models import *
from openunipay.weixin_pay.models import *
from openunipay.util import datetime
from datetime import timedelta

PAY_WAY_WEIXIN = 'WEIXIN'
PAY_WAY_ALI = 'ALI'
PAY_WAY = ((PAY_WAY_WEIXIN, u'微信支付'), (PAY_WAY_ALI, u'支付宝支付'),)


class OrderItem(models.Model):
    orderno = models.CharField(verbose_name=u'订单号', max_length=50, primary_key=True, editable=False)
    user = models.CharField(verbose_name=u'用户标识', max_length=50, null=True, blank=True)
    product_desc = models.CharField(verbose_name=u'商品描述', max_length=128, null=False, blank=False)
    product_detail = models.TextField(verbose_name=u'商品详情', max_length=1000, null=False, blank=False)
    fee = models.DecimalField(verbose_name=u'金额(单位:分)', max_digits=6, decimal_places=0, null=False, blank=False)
    attach = models.CharField(verbose_name=u'附加数据', max_length=127, null=True, blank=True)
    dt_start = models.DateTimeField(verbose_name=u'交易开始时间', null=False, blank=False, editable=False)
    dt_end = models.DateTimeField(verbose_name=u'交易失效时间', null=False, blank=False, editable=False)
    dt_pay = models.DateTimeField(verbose_name=u'付款时间', null=True, blank=True, editable=False)
    paied = models.BooleanField(verbose_name=u'已收款', null=False, blank=False, default=False, editable=False)
    lapsed = models.BooleanField(verbose_name=u'已失效', null=False, blank=False, default=False, editable=False)
    payway = models.CharField(verbose_name=u'支付方式', max_length=10, null=False, blank=False, choices=PAY_WAY, default=PAY_WAY[0][0])
    date_create = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    date_update = models.DateTimeField(verbose_name=u'修改时间', auto_now=True)
    
    
    class Meta:
        verbose_name = '付款单'
        verbose_name_plural = '付款单'
        
    def __str__(self):
        return self.orderno
        
    def _set_expire_time(self, expire):
        self.dt_start = datetime.local_now()
        self.dt_end = self.dt_start + timedelta(minutes=expire)
        
    def initial_orlder(self, expire):
        self._set_expire_time(expire)
