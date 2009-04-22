#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from paypal.standard.pdt.models import PayPalPDT
from paypal.standard.forms import PAYPAL_DATE_FORMAT 


class PayPalPDTForm(forms.ModelForm):
    """Form used to receive and record PayPal Return Data Transfers."""
    # PayPal dates have non-standard formats.
    payment_date = forms.DateTimeField(required=False, input_formats=PAYPAL_DATE_FORMAT)
    next_payment_date = forms.DateTimeField(required=False, input_formats=PAYPAL_DATE_FORMAT)

    class Meta:
        model = PayPalPDT


