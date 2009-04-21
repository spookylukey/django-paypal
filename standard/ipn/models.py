#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.http import urlencode
from django.http import QueryDict
import urllib2
from urllib import unquote_plus
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
import logging
from django.test.client import Client
from django.core.urlresolvers import reverse
from paypal.standard.models import PayPalStandardBase, POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT

class PayPalIPN(PayPalStandardBase):
    """
    Logs PayPal IPN interactions.    
    
    """

    class Meta:
        db_table = "paypal_ipn"
        verbose_name = "PayPal IPN"

    def __unicode__(self):
        fmt = u"<IPN: %s %s>"
        if self.is_transaction():
            return fmt % ("Transaction", self.txn_id)
        else:
            return fmt % ("Recurring", self.recurring_payment_id)
        
    
        
    def _postback(self, test=True):
        """
        Perform PayPal Postback validation.
        Sends the received data back to PayPal which responds with verified or invalid.
        Flags the payment if the response is invalid.
        Returns True if the postback is verified.
        
        """
        response = ""
        if hasattr(settings, 'PAYPAL_TESTING'):
            client = Client()
            paypal_http_response = client.get(reverse('paypal-fake-ipn-response'))
            response = paypal_http_response.content.strip()
        else:
            import urllib2
            if test:
                endpoint = SANDBOX_POSTBACK_ENDPOINT
            else:
                endpoint = POSTBACK_ENDPOINT
            response = urllib2.urlopen(endpoint, "cmd=_notify-validate&%s" % self.query).read()
        if response == "VERIFIED":
            return True
        else:
            self.set_flag("Invalid postback.")
            return False
        
    def send_signals(self, result):  
        if self.flag:
            payment_was_flagged.send(sender=self)
        else:
            payment_was_successful.send(sender=self)    

    def init(self, request):
        self.query = request.POST.urlencode()
        self.ipaddress = request.META.get('REMOTE_ADDR', '')
