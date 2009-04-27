#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib import unquote_plus
import urllib2
from django.db import models
from django.conf import settings
from django.http import QueryDict
from django.utils.http import urlencode
from paypal.standard.models import PayPalStandardBase
from paypal.standard.pdt.signals import pdt_failed, pdt_successful

# ### Todo: Move this logic to conf.py:
# if paypal.standard.pdt is in installed apps
# ... then check for this setting in conf.py
class PayPalSettingsError(Exception):
    """Raised when settings are incorrect."""

if not hasattr(settings.PAYPAL_IDENTITY_TOKEN):
    raise PayPalSettingsError("You must set PAYPAL_IDENTITY_TOKEN in settings.py. Get this token by enabling PDT in your PayPal account.")
IDENTITY_TOKEN = settings.PAYPAL_IDENTITY_TOKEN



class PayPalPDT(PayPalStandardBase):
    amt = models.DecimalField(max_digits=64, decimal_places=2, default=0, blank=True, null=True)
    cm = models.CharField(max_length=255, blank=True)
    sig = models.CharField(max_length=255, blank=True)
    tx = models.CharField(max_length=255, blank=True)
    st = models.CharField(max_length=32, blank=True)
    
    class Meta:
        db_table = "paypal_pdt"
        verbose_name = "PayPal PDT"

    def __unicode__(self):
        fmt = u"<PDT: %s %s>"
        if self.is_transaction():
            return fmt % ("Transaction", self.txn_id)
        else:
            return fmt % ("Recurring", self.recurring_payment_id)

    def _postback(self, test=True):
        """
        Perform PayPal PDT Postback validation.
        Sends the transaction ID and business token to PayPal which responses with
        SUCCESS or FAILED.
        
        """
        postback_dict = dict(cmd="_notify-synch", at=IDENTITY_TOKEN, tx=self.tx)
        postback_params = urlencode(postback_dict)
        response = urllib2.urlopen(self.get_endpoint(test), postback_params).read()
        return response
    
    def _verify_postback(self, response):
        from paypal.standard.pdt.forms import PayPalPDTForm
        result = False
        response_list = response.split('\n')
        response_dict = {}
        for i, line in enumerate(response_list):
            unquoted_line = unquote_plus(line).strip()        
            if i == 0:
                self.st = unquoted_line
                if self.st == "SUCCESS":
                    result = True
            else:
                if self.st != "SUCCESS":
                    self.set_flag(line)
                    break
                try:                        
                    if not unquoted_line.startswith(' -'):
                        k, v = unquoted_line.split('=')                        
                        response_dict[k.strip()] = v.strip()
                except ValueError, e:
                    pass
        
        qd = QueryDict('', mutable=True)
        qd.update(response_dict)
        qd.update(dict(ipaddress=self.ipaddress, st=self.st, flag_info=self.flag_info))
        pdt_form = PayPalPDTForm(qd, instance=self)
        pdt_form.save(commit=False)        
        return result
  
    def send_signals(self, result):
        if result:
            pdt_successful.send(sender=self)
        else:
            pdt_failed.send(sender=self)