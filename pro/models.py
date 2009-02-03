#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string

from django.db import models
from django.forms.models import model_to_dict

from paypal.pro.fields import CountryField

L = string.split

# ### ToDo: Remove PaymentInfo models. and flesh out NVP model.
# ### they duplicate information!

class PayPalNVP(models.Model):

    # 2009-02-03T17:47:41Z
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    RESTRICTED_FIELDS = "expdate cvv2 acct".split()
    ADMIN_FIELDS = L("id user flag flag_code flag_info query response created_at updated_at ")
    ITEM_FIELDS = L("amt custom invnum")
    DIRECT_FIELDS = L("firstname lastname street city state countrycode zip")

    # Response fields
    method = models.CharField(max_length=16, blank=True)
    ack = models.CharField(max_length=16, blank=True)    
    profilestatus = models.CharField(max_length=32, blank=True)
    # ### ToDo: Unpacking this field from the paypal time is giving weird erros.
    # timestamp = models.DateTimeField(blank=True, null=True)
    profileid = models.CharField(max_length=16, blank=True)  # I-E596DFUSD882
    correlationid = models.CharField(max_length=16, blank=True) # 25b380cda7a21
    token = models.CharField(max_length=64, blank=True)
    payerid = models.CharField(max_length=64, blank=True)
    
    # Transaction Fields
    firstname = models.CharField("First Name", max_length=255, blank=True)
    lastname = models.CharField("Last Name", max_length=255, blank=True)
    street = models.CharField("Street Address", max_length=255, blank=True)
    city = models.CharField("City", max_length=255, blank=True)
    state = models.CharField("State", max_length=255, blank=True)
    countrycode = CountryField("Country", default="US", blank=True)
    zip = models.CharField("Postal / Zip Code", max_length=32, blank=True)
    
    # Custom fields
    invnum = models.CharField(max_length=255, blank=True)
    custom = models.CharField(max_length=255, blank=True) 
    
    # Admin fields
    user = models.ForeignKey('auth.user', blank=True, null=True)
    flag = models.BooleanField(default=False, blank=True)
    flag_code = models.CharField(max_length=16, blank=True)
    flag_info = models.TextField(blank=True)    
    ipaddress = models.IPAddressField(blank=True)
    query = models.TextField(blank=True)
    response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        
    class Meta:
        db_table = "paypal_nvp"
    
    def init(self, request, params, response):
        """
        Initialize a PayPalNVP instance from a HttpRequest object.
        
        """
        self.ipaddress = request.META.get('REMOTE_ADDR', '')
        if request.user.is_authenticated():
            self.user = request.user
        # No storing that CC# info. Bad.
        query_data = dict((k,v) for k, v in params.iteritems() if k not in self.RESTRICTED_FIELDS)
        self.query = repr(query_data)
        self.response = repr(response)

        # Was there a flag on the play?        
        if response.get('ack', False) != "Success":
            self.set_flag(response.get('L_LONGMESSAGE0', ''), response.get('L_ERRORCODE0', ''))

    def set_flag(self, info, code=None):
        """Flag this PaymentInfo for further investigation."""
        self.flag = True
        self.flag_info += info
        if code is not None:
            self.flag_code = code

    def process(self, request, item):
        """
        Do a direct payment.
        
        """
        from paypal.pro.helpers import PayPalWPP
        wpp = PayPalWPP(request)

        # Change the model information into a dict that PayPal can understand.        
        params = model_to_dict(self, exclude=self.ADMIN_FIELDS)
        params['acct'] = self.acct
        params['creditcardtype'] = self.creditcardtype
        params['expdate'] = self.expdate
        params['cvv2'] = self.cvv2
        params.update(item)      

        # Create single payment:
        if 'billingperiod' not in params:
            return wpp.doDirectPayment(params)
        # Create recurring payment:
        else:
            return wpp.createRecurringPaymentsProfile(params, direct=True)