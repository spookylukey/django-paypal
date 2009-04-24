#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from paypal.standard.ipn.forms import PayPalIPNForm
from paypal.standard.ipn.models import PayPalIPN

def handle_ipn_post(request, item_check_callable=None, from_view='notify'):
    """Naive wrapper for ipn view, so we can set the view whence the ipn came from
    """

    form = PayPalIPNForm(request.POST)
    if form.is_valid():
        try:
            ipn_obj = form.save(commit=False)
        except Exception, e:
            ipn_obj = PayPalIPN()
            ipn_obj.set_flag("Exception while processing. (%s)" % form.errors)
    else:
        ipn_obj.set_flag("Invalid form. (%s)" % form.errors)

    # notify/return/cancel
    ipn_obj.from_view = from_view

    ipn_obj.initialize(request)
    if not ipn_obj.flag:
        # Secrets should only be used over SSL.
        if request.is_secure() and 'secret' in request.GET:
            ipn_obj.verify_secret(form, request.GET['secret'])
        else:
            ipn_obj.verify(item_check_callable)

    return ipn_obj

@require_POST
def ipn(request, item_check_callable=None):
    """
    PayPal IPN endpoint (notify_url).
    Used by both PayPal Payments Pro and Payments Standard to confirm transactions.
    http://tinyurl.com/d9vu9d
    
    PayPal IPN Simulator:
    https://developer.paypal.com/cgi-bin/devscr?cmd=_ipn-link-session
    
    """    

    ipn_obj = handle_ipn_post(request, item_check_callable=item_check_callable, from_view='notify')

    ipn_obj.save()
    return HttpResponse("OKAY")

