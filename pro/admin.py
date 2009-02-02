#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin

from paypal.pro.models import PayPalPaymentInfo


class PayPalPaymentInfoAdmin(admin.ModelAdmin):
    pass
#     date_hierarchy = 'payment_date'
#     fieldsets = (
#         (None, {
#             "fields": ('flag', 'txn_id', 'payment_status', 'payment_date', 'transaction_entity', 'reason_code', 'pending_reason', 'mc_gross', 'auth_status', 'auth_amount', 'auth_exp', 'auth_id',)
#         }),
#         ("Address", {
#             "description": "The address of the Buyer.",
#             'classes': ('collapse',),
#             "fields": ('address_city', 'address_country', 'address_country_code', 'address_name', 'address_state', 'address_status', 'address_street', 'address_zip',)
#         }),
#         ("Buyer", {
#             "description": "The information about the Buyer.",
#             'classes': ('collapse',),
#             "fields": ('first_name', 'last_name', 'payer_business_name', 'payer_email', 'payer_id', 'payer_status', 'contact_phone', 'residence_country',)    
#         }),
#         ("Seller", {
#             "description": "The information about the Seller.",
#             'classes': ('collapse',),
#             "fields": ('business', 'item_name', 'item_number', 'quantity', 'receiver_email', 'receiver_id', 'custom', 'invoice', 'memo',)        
#         }),
#         ("Admin", {
#             "description": "Additional Info.",
#             "classes": ('collapse',),
#             "fields": ('test_ipn', 'ip', 'query',)
#         }),
#     )
#     list_display = ('__unicode__', 'txn_id', 'flag', 'payment_status', 'payment_date', )
admin.site.register(PayPalPaymentInfo, PayPalPaymentInfoAdmin)
