#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST, require_GET
from paypal.standard.ipn.forms import PayPalIPNForm
from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.models import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT
from urllib import unquote_plus
import urllib2
import logging

# PayPal IPN Simulator:
# https://developer.paypal.com/cgi-bin/devscr?cmd=_ipn-link-session

@require_POST
def ipn(request, item_check_callable=None):
    """
    PayPal IPN endpoint (notify_url).
    Used by both PayPal Payments Pro and Payments Standard to confirm transactions.
    https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/howto_html_instantpaymentnotif
    
    """    
    form = PayPalIPNForm(request.POST)
    failed = False    
    if form.is_valid():
        try:
            ipn_obj = form.save(commit=False)
        except Exception, e:
            error = repr(e)
            failed = True
            logging.error(error)
    else:
        error = form.errors
        failed = True
        logging.error(error)
        
    if failed:
        ipn_obj = PayPalIPN()
        ipn_obj.set_flag("Invalid form. %s" % error)
    
    ipn_obj.init(request)

    if not failed:
        # Secrets should only be used over SSL.
        if request.is_secure() and 'secret' in request.GET:
            ipn_obj.verify_secret(form, request.GET['secret'])
        else:
            if ipn_obj.test_ipn:
                ipn_obj.verify(item_check_callable)
            else:
                ipn_obj.verify(item_check_callable, test=False)
    
    return HttpResponse("OKAY")
