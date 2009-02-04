#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin

from paypal.pro.models import PayPalNVP


class PayPalNVPAdmin(admin.ModelAdmin):
    list_display = "user method flag flag_code created_at".split()
admin.site.register(PayPalNVP, PayPalNVPAdmin)
