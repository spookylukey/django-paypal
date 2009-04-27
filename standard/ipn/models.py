#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
from paypal.standard.models import PayPalStandardBase


class PayPalIPN(PayPalStandardBase):
    """Logs PayPal IPN interactions."""
    FORMAT = u"<IPN: %s %s>"

    class Meta:
        db_table = "paypal_ipn"
        verbose_name = "PayPal IPN"

    def _postback(self):
        """Perform PayPal Postback validation."""
        self.response = urllib2.urlopen(self.get_endpoint(), "cmd=_notify-validate&%s" % self.query).read()
    
    def _verify_postback(self):
        if self.response != "VERIFIED":
            self.set_flag("Invalid postback. (%s)" % self.response)