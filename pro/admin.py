#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin

from paypal.pro.models import PayPalPaymentInfo, PayPalNVP

# ### ToDo: payment info model must go...
class PayPalPaymentInfoAdmin(admin.ModelAdmin):
    pass
admin.site.register(PayPalPaymentInfo, PayPalPaymentInfoAdmin)

class PayPalNVPAdmin(admin.ModelAdmin):
    list_display = "user ipaddress flag flag_code created_at".split()
admin.site.register(PayPalNVP, PayPalNVPAdmin)
