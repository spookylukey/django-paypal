#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from paypal.standard.forms import PayPalStandardBaseForm
from paypal.standard.pdt.models import PayPalPDT


class PayPalPDTForm(PayPalStandardBaseForm):
    class Meta:
        model = PayPalPDT
        exclude = ['ipaddress', 'flag', 'flag_code',
                   'flag_info', 'query', 'response',
                   'created_at', 'updated', 'form_view']


class PayPalPDTCallbackForm(forms.ModelForm):
    class Meta:
        model = PayPalPDT
        fields = ['amt', 'cm', 'tx', 'st']
