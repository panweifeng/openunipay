# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import AliPayOrder
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class AliPayOrderResource(resources.ModelResource):
    class Meta:
        model = AliPayOrder
        import_id_fields = ('id',)

class AliPayOrderAdmin(ImportExportModelAdmin):
    resource_class = AliPayOrderResource
    # list page
    list_display = ('date_create', 'out_trade_no', 'subject', 'body', 'total_fee', 'it_b_pay', 'get_pay_result',)
    ordering = ('-date_create',)
    search_fields = ['=out_trade_no', ]
    
    def get_pay_result(self, obj):
        if hasattr(obj, 'pay_result'):
            return obj.pay_result
        else:
            return '-'
    get_pay_result.short_description = '支付结果'
    
    
admin.site.register(AliPayOrder, AliPayOrderAdmin)
