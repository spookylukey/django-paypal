#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.forms.util import flatatt
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings

from paypal.standard.widgets import ValueHiddenInput, ReservedValueHiddenInput
from paypal.standard.pdt.models import PayPalPDT
from paypal.standard.forms import PAYPAL_DATE_FORMAT 

class PayPalPDTForm(forms.ModelForm):
    """
    Form used to receive and record PayPal Return Data Transfers.
    """
    # PayPal dates have non-standard formats.
    payment_date = forms.DateTimeField(required=False, input_formats=PAYPAL_DATE_FORMAT)
    next_payment_date = forms.DateTimeField(required=False, input_formats=PAYPAL_DATE_FORMAT)

    class Meta:
        model = PayPalPDT


