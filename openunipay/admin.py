# -*- coding: utf-8 -*-
from django.contrib import admin
from .ali_pay.admin import *
from .weixin_pay.admin import *

from .models import OrderItem

class OrderItemResource(resources.ModelResource):
    class Meta:
        model = OrderItem
        import_id_fields = ('orderno',)

class OrderItemAdmin(ImportExportModelAdmin):
    resource_class = OrderItemResource
    # list page
    list_display = ('orderno', 'user', 'product_desc', 'payway', 'fee', 'dt_start', 'dt_end', 'dt_pay', 'paied')
    ordering = ('-dt_start',)
    search_fields = ['=orderno', '=user', ] 
    list_filter = ('payway', 'paied', 'product_desc',)
    
    def save_model(self, request, obj, form, change):
        if not obj.orderno:
            obj.initial_orlder()
        admin.ModelAdmin.save_model(self, request, obj, form, change) 
        
        
admin.site.register(OrderItem, OrderItemAdmin)

