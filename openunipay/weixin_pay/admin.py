# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import WeiXinOrder
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class WeiXinOrderResource(resources.ModelResource):
    class Meta:
        model = WeiXinOrder
        import_id_fields = ('id',)

class WeiXinOrderAdmin(ImportExportModelAdmin):
    resource_class = WeiXinOrderResource
    # list page
    list_display = ('out_trade_no', 'body', 'attach', 'fee_type', 'total_fee', 'spbill_create_ip', 'time_start', 'time_expire', 'trade_type', 'get_pay_result')
    ordering = ('time_start',)
    search_fields = ['=out_trade_no', '=spbill_create_ip', ]
    
    def get_pay_result(self, obj):
        if hasattr(obj, 'pay_result'):
            return obj.pay_result
        else:
            return '-'
    get_pay_result.short_description = '支付结果'
    
    
admin.site.register(WeiXinOrder, WeiXinOrderAdmin)
