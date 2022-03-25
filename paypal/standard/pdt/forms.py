#!/usr/bin/env python

from paypal.standard.forms import PayPalStandardBaseForm
from paypal.standard.pdt.models import PayPalPDT


class PayPalPDTForm(PayPalStandardBaseForm):
    class Meta:
        model = PayPalPDT
        exclude = [
            "ipaddress",
            "flag",
            "flag_code",
            "flag_info",
            "query",
            "response",
            "created_at",
            "updated",
            "form_view",
        ]
