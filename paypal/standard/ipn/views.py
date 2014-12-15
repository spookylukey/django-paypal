#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse, QueryDict
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from .forms import PayPalIPNForm
from .models import PayPalIPN


class IPNView(View):
    """
    PayPal IPN endpoint (notify_url).
    Used by both PayPal Payments Pro and Payments Standard to confirm transactions.
    http://tinyurl.com/d9vu9d

    PayPal IPN Simulator:
    https://developer.paypal.com/cgi-bin/devscr?cmd=_ipn-link-session
    """
    def __init__(self):
        self.post_data = None
        self.flag = None
        self.ipn_obj = None
        self.form = None

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(IPNView, self).dispatch(*args, **kwargs)

    def post(self, request, item_check_callable=None):
        self.set_post_data()
        self.clear_invalid_dates_in_post_data() if self.post_data else None
        self.create_ipn_obj() if self.post_data else None
        self.save_ipn_obj(item_check_callable)
        self.ipn_obj.send_signals()
        return HttpResponse("OKAY")

    def set_post_data(self):
        # Need to cope with custom encoding, which is stored in the body (!).
        # Assuming the tolerant parsing of QueryDict and an ASCII-like encoding,
        # such as windows-1252, latin1 or UTF8, the following will work:
        encoding = self.request.POST.get('charset', None)
        if not encoding:
            self.flag = "Invalid form - no charset passed, can't decode"
        else:
            try:
                self.post_data = QueryDict(self.request.body, encoding=encoding).copy()
            except LookupError:
                self.flag = "Invalid form - invalid charset"

    def create_ipn_obj(self):
        self.form = PayPalIPNForm(self.post_data)
        if self.form.is_valid():
            try:
                self.ipn_obj = self.form.save(commit=False)
            except Exception as e:
                self.flag = "Exception while processing. (%s)" % e
        else:
            self.flag = "Invalid form. (%s)" % self.form.errors

    def clear_invalid_dates_in_post_data(self):
        # Clean up the data as PayPal sends some weird values such as "N/A".
        date_fields = ('time_created', 'payment_date', 'next_payment_date',
                       'subscr_date', 'subscr_effective')
        for date_field in date_fields:
            if self.post_data.get(date_field) == 'N/A':
                del self.post_data[date_field]

    def save_ipn_obj(self, item_check_callable):
        self.ipn_obj = PayPalIPN() if not self.ipn_obj else self.ipn_obj
        self.ipn_obj.initialize(self.request)
        self.ipn_obj.set_flag(self.flag) if self.flag else self.verify(item_check_callable)
        self.ipn_obj.save()

    def verify(self, item_check_callable):
        if self.request.is_secure() and 'secret' in self.request.GET:
            self.ipn_obj.verify_secret(self.form, self.request.GET['secret'])
        else:
            self.ipn_obj.verify(item_check_callable)
