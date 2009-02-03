#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.forms.models import model_to_dict

from paypal.pro.fields import CountryField
from paypal.pro.signals import payment_was_successful, payment_was_flagged

# ### ToDo: Move all signalling to IPN.

# ### ToDo: A lot of these common fields could be moved to mixins.
# ### there is a lot of non-dry stuff going on between the models here.

# ### ToDo: Need a better way to store responses and more information from a transaction
# ### can we use the iPN model in standard?

# ### ToDo: flesh out NVP request / response model for WPP interactios.

class PayPalNVP(models.Model):
    user = models.ForeignKey('auth.user', null=True)
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
    
    def init(self, request, query, response):
        """Initialize a PayPalNVP instance from a HttpRequest object."""
        self.ipaddress = request.META.get('REMOTE_ADDR', '')
        if request.user.is_authenticated():
            self.user = request.user
        self.query = repr(query)
        self.response = repr(response)

    def set_flag(self, info, code=None):
        """Flag this PaymentInfo for further investigation."""
        self.flag = True
        self.flag_info += info
        if code is not None:
            self.flag_code = code


class BasePaymentInfo(models.Model):
    """
    Base model suitable for representing a payment!    

    """
    firstname = models.CharField("First Name", max_length=255)
    lastname = models.CharField("Last Name", max_length=255)
    street = models.CharField("Street Address", max_length=255)
    city = models.CharField("City", max_length=255)
    state = models.CharField("State", max_length=255)
    countrycode = CountryField("Country", default="US")
    zip = models.CharField("Zipcode", max_length=32)

    class Meta:
        abstract = True
        
class PaymentInfo(BasePaymentInfo):
    """
    Payment model with a bit more information.

    """
    RESTRICTED_FIELDS = "expdate_0 expdate_1 cvv2 acct".split()

    # Admin fields:        
    user = models.ForeignKey('auth.user', null=True)
    ipaddress = models.IPAddressField(blank=True)
    flag = models.BooleanField(default=False, blank=True)
    flag_code = models.CharField(max_length=16, blank=True)
    flag_info = models.TextField(blank=True)
    query = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
    def init(self, request):
        """Initialize a PaymentInfo instance from a HttpRequest object."""
        self.ipaddress = request.META.get('REMOTE_ADDR', '')
        # No storing that CC# info. Bad.
        query_data = dict((k,v) for k, v in request.POST.iteritems() if k not in self.RESTRICTED_FIELDS)
        self.query = repr(query_data)
        if request.user.is_authenticated():
            self.user = request.user

    def set_flag(self, info, code=None):
        """Flag this PaymentInfo for further investigation."""
        self.flag = True
        self.flag_info += info
        if code is not None:
            self.flag_code = code


class PayPalPaymentInfo(PaymentInfo):
    """
    Payment model with paypal attack methods.
    
    """
    ADMIN_FIELDS = "id user ipaddress flag flag_code flag_info query created_at updated_at response".split()
    ITEM_FIELDS = "amt custom invnum".split()
    
    amt = models.FloatField(blank=True, null=True)
    custom = models.CharField(max_length=255, blank=True)
    invnum = models.CharField(max_length=127, blank=True)
    response = models.TextField(blank=True)
    
    class Meta:
        db_table = "paypal_paymentinfo"
        
    def process(self, request, item):
        """
        Do a direct payment.
        
        """
        from paypal.pro.helpers import PayPalWPP
        wpp = PayPalWPP(request)

        # Change the model information into a dict that PayPal can understand.        
        params = model_to_dict(self, exclude=self.ADMIN_FIELDS)
        params['ipaddress'] = self.ipaddress  # These were stashed in form.save.
        params['acct'] = self.acct
        params['creditcardtype'] = self.creditcardtype
        params['expdate'] = self.expdate
        params['cvv2'] = self.cvv2
        params.update(item)      

        # Create single payment:
        if 'billingperiod' not in params:
            response = wpp.doDirectPayment(params)
        # Create recurring payment:
        else:
            response = wpp.createRecurringPaymentsProfile(params, direct=True)

        # Store the response.
        self.response = repr(response)
        
        # ### ToDo: This duplicates the new PayPalNVP class - remove the data here, or elsewhere.
        # ### ToDo: Can these signals instead be sent out by the IPN ???
        if response['ACK'] != "Success":
            self.set_flag(response.get('L_LONGMESSAGE0', ''), response.get('L_ERRORCODE0', ''))
#            payment_was_flagged.send(sender=self, response=response, request=request)
            return False
        else:
#            payment_was_successful.send(sender=self, response=response, request=request)
            return True