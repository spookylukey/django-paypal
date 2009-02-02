#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms

from paypal.pro.models import PayPalPaymentInfo
from paypal.pro.fields import CreditCardField, CreditCardExpiryField, CreditCardCVV2Field, COUNTRIES


class PaymentForm(forms.ModelForm):
    acct = CreditCardField(label="Credit Card Number")
    expdate = CreditCardExpiryField(label="Expiry Date")
    cvv2 = CreditCardCVV2Field(label="CVV2")

    class Meta:
        model = PayPalPaymentInfo
        exclude = PayPalPaymentInfo.ADMIN_FIELDS + PayPalPaymentInfo.ITEM_FIELDS

    def save(self, commit=False):
        instance = super(PaymentForm, self).save(commit)
        if not commit:
            instance.acct = self.cleaned_data['acct']
            instance.creditcardtype = self.fields['acct'].card_type
            instance.cvv2 = self.cleaned_data['cvv2']
            instance.expdate = self.cleaned_data['expdate'].strftime("%m%Y")
        return instance