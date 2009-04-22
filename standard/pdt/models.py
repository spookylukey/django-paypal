#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
from django.db import models
from django.conf import settings
from django.http import QueryDict
from django.utils.http import urlencode
from paypal.standard.models import PayPalStandardBase
from paypal.standard.pdt.signals import pdt_failed, pdt_successful
from urllib import unquote_plus

if not settings.PAYPAL_IDENTITY_TOKEN:
    raise Exception("You must set settings.PAYPAL_IDENTITY_TOKEN in settings.py, you can get this token by enabling PDT in your paypal business account")
IDENTITY_TOKEN = settings.PAYPAL_IDENTITY_TOKEN


class PayPalPDT(PayPalStandardBase):
    amt = models.FloatField(default=0, blank=True, null=True)
    cm = models.CharField(max_length=255, blank=True)
    sig = models.CharField(max_length=255, blank=True)
    tx = models.CharField(max_length=255, blank=True)
    st = models.CharField(max_length=32, blank=True)
    
    class Meta:
        db_table = "paypal_pdt"
        verbose_name = "PayPal PDT"
    
    def init(self, request):
        self.query = request.GET.urlencode()
        self.ipaddress = request.META.get('REMOTE_ADDR', '')

    def _postback(self, test=True):
        """
        Perform PayPal PDT Postback validation.
        Sends the transaction id and busines paypal token data back to PayPal which responds with SUCCESS or FAILED.
        Returns True if the postback is successful.
        
        """
        postback_dict = dict(cmd="_notify-synch", at=IDENTITY_TOKEN, tx=self.tx)
        postback_params = urlencode(postback_dict)
        response = urllib2.urlopen(self.get_endpoint(test), postback_params).read()
        return self._parse_paypal_response(response)
    
    def _parse_paypal_response(self, response):
        # ### Could this function be cleaned up a bit?
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
                    # ### What's going to happen if there are multiple errors?
                    self.set_flag(line)
            else:
                try:                        
                    if not unquoted_line.startswith(' -'):
                        k, v = unquoted_line.split('=')                        
                        response_dict[k.strip()] = v.strip()
                # ### Why would this happen?
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
                    
    
    def __unicode__(self):
        fmt = u"<PDT: %s %s>"
        if self.is_transaction():
            return fmt % ("Transaction", self.txn_id)
        else:
            return fmt % ("Recurring", self.recurring_payment_id)
    