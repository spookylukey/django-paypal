#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.http import urlencode
from django.http import QueryDict
import urllib2
from urllib import unquote_plus
from paypal.standard.pdt.signals import pdt_failed, pdt_successful
import logging
from django.test.client import Client
from django.core.urlresolvers import reverse
from paypal.standard.models import PayPalStandardBase, POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT
        
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
        if not settings.PAYPAL_IDENTITY_TOKEN:
            raise Exception("You must set settings.PAYPAL_IDENTITY_TOKEN in settings.py, you can get this token by enabling PDT in your paypal business account")
        
        paypal_response = ""
        postback_dict={}    
        postback_dict["cmd"]="_notify-synch"
        postback_dict["at"]=settings.PAYPAL_IDENTITY_TOKEN    
        postback_dict["tx"]=self.tx    
        postback_params=urlencode(postback_dict)
        
        PP_URL = POSTBACK_ENDPOINT
        if settings.DEBUG:
            PP_URL = SANDBOX_POSTBACK_ENDPOINT
    
        if hasattr(settings, 'PAYPAL_TESTING'):
            client = Client()
            paypal_http_response = client.get(reverse('paypal-fake-pdt-response'), {'custom': self.cm, 'txn_id': self.tx, 'mc_gross': self.amt})
            paypal_response = paypal_http_response.content
        else:
            req = urllib2.Request(PP_URL)
            req.add_header("Content-type", "application/x-www-form-urlencoded")
            fo = urllib2.urlopen(PP_URL, postback_params)
            paypal_response = fo.read()
            fo.close()
            
        logging.debug(paypal_response)
        
        result = self._parse_paypal_response(paypal_response)
        return result
    
    def _parse_paypal_response(self, paypal_response):
        from forms import PayPalPDTForm
        result = False
        paypal_response_list = paypal_response.split('\n')
    
        paypal_response_dict = {}
        i = 0
        for paypal_line in paypal_response_list:
            unquoted_paypal_line = unquote_plus(paypal_line)        
            if i == 0:
                self.st = unquoted_paypal_line.strip()
            else:
                if self.st == 'SUCCESS':
                    result = True
                    try:                        
                        if not unquoted_paypal_line.startswith(' -'):
                            [k, v] = unquoted_paypal_line.split('=')                        
                            paypal_response_dict[k.strip()]=v.strip()
                    except ValueError, e:
                        logging.error("comfirm_pay_pal error, %s, %s"%(e, unquoted_paypal_line))
                else:
                    self.set_flag(paypal_line)
                    logging.error('transaction_status = %s'%self.st)
            i = i + 1  
        
        fake_query_dict = QueryDict('', mutable=True)
        fake_query_dict.update(paypal_response_dict)
        fake_query_dict.update({'ipaddress': self.ipaddress, 'st': self.st, 'flag_info': self.flag_info})
        pdt_form = PayPalPDTForm(fake_query_dict, instance=self)
        pdt_form.save(commit=False)
        
        return result
  
    
    def send_signals(self, result):
        if result == True:
            pdt_successful.send(sender=self)
        else:
            pdt_failed.send(sender=self)        
                    
    
    def __unicode__(self):
        fmt = u"<PDT: %s %s>"
        if self.is_transaction():
            return fmt % ("Transaction", self.txn_id)
        else:
            return fmt % ("Recurring", self.recurring_payment_id)
    