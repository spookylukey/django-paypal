#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from paypal.standard.widgets import ValueHiddenInput, ReservedValueHiddenInput
from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.forms import PAYPAL_DATE_FORMAT 


class PayPalIPNForm(forms.ModelForm):
    """
    Form used to receive and record PayPal IPN notifications.
    
    PayPal IPN test tool:
    https://developer.paypal.com/us/cgi-bin/devscr?cmd=_tools-session    
    
    """
    # PayPal dates have non-standard formats.
    payment_date = forms.DateTimeField(required=False, input_formats=PAYPAL_DATE_FORMAT)
    next_payment_date = forms.DateTimeField(required=False, input_formats=PAYPAL_DATE_FORMAT)

    class Meta:
        model = PayPalIPN

