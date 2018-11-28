#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests

from paypal.standard.ipn.signals import invalid_ipn_received, valid_ipn_received
from paypal.standard.models import PayPalStandardBase


class PayPalIPN(PayPalStandardBase):
    """Logs PayPal IPN interactions."""
    format = u"<IPN: %s %s>"

    class Meta:
        db_table = "paypal_ipn"
        verbose_name = "PayPal IPN"

    def _postback(self):
        """Perform PayPal Postback validation."""
        return requests.post(self.get_endpoint(), data=b"cmd=_notify-validate&" + self.query.encode("ascii")).content

    def _verify_postback(self):
        if self.response != "VERIFIED":
            self.set_flag("Invalid postback. ({0})".format(self.response))

    def send_signals(self):
        """Shout for the world to hear whether a txn was successful."""
        if self.flag:
            invalid_ipn_received.send(sender=self)
            return
        else:
            valid_ipn_received.send(sender=self)

    def __repr__(self):
        return '<PayPalIPN id:{0}>'.format(self.id)

    def __str__(self):
        return "PayPalIPN: {0}".format(self.id)
