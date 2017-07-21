# -*- coding: utf-8 -*-
from django.contrib import admin
from .ali_pay.admin import *
from .weixin_pay.admin import *

from .models import OrderItem, Product, PAY_WAY_WEIXIN
from openunipay.paygateway import unipay


class OrderItemResource(resources.ModelResource):
    class Meta:
        model = OrderItem
        import_id_fields = ('orderno', )


class OrderItemAdmin(ImportExportModelAdmin):
    resource_class = OrderItemResource
    # list page
    list_display = ('orderno', 'user', 'product_desc', 'payway', 'fee', 'dt_start', 'dt_end', 'dt_pay', 'paied')
    ordering = ('-dt_start', )
    search_fields = ['=orderno',
                     '=user', ]
    list_filter = ('payway',
                   'paied',
                   'product_desc', )

    def save_model(self, request, obj, form, change):
        if not obj.orderno:
            obj.initial_orlder()
        admin.ModelAdmin.save_model(self, request, obj, form, change)


########################### product #########################
class ProductResource(resources.ModelResource):
    class Meta:
        model = OrderItem
        import_id_fields = ('productid', )


class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    # list page
    list_display = ('productid',
                    'product_desc',
                    'fee',
                    'weinxin_qrurl',
                    'date_create',
                    'date_update', )
    ordering = ('-date_create', )
    search_fields = ['=productid', ]

    def save_model(self, request, obj, form, change):
        obj.weinxin_qrurl = unipay.generate_qr_pay_url(PAY_WAY_WEIXIN, obj.productid)
        admin.ModelAdmin.save_model(self, request, obj, form, change)


admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Product, ProductAdmin)
