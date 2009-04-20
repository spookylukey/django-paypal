#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST, require_GET
from django.core.exceptions import ObjectDoesNotExist
from paypal.standard.forms import *
from paypal.standard.models import PayPalIPN
from models import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT
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

@require_GET
def pdt(request, item_check_callable=None):
    """
    Payment data transfer implementation
    https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/howto_html_paymentdatatransfer
    e.g. url
    http://www.yoursite.com/ad/payment/complete?tx=4WJ86550014687441&st=Completed&amt=225.00&cc=EUR&cm=a3e192b8%2d8fea%2d4a86%2db2e8%2dd5bf502e36be&item_number=&sig=LFeVvU3hPqTy6m7mN%2bqarxpZLII%2fiDgNyjBWaxhfWDBFiFW%2b%2bZnW8WzSwbH4Ja8K%2bSXsoQHOlV5V0YtJM%2fVdHaQmXlEWz8endvh2pOiYthgVAH%2bL32OTML1YSJrrQZvz5eF2bo9v0gPasxOwiHgQ%2bzeLos3fU4X2FTw2JxnB%2fQ4%3d
    """
    
    txn_id = request.GET.get('tx', None)
    if txn_id is not None:
        try:
            pdt_obj = PayPalPDT.objects.get(txn_id=txn_id)
        except ObjectDoesNotExist, e:
            form = PayPalPDTForm(request.GET)
            failed = False    
            if form.is_valid():
                try:
                    pdt_obj = form.save(commit=False)
                except Exception, e:
                    error = repr(e)
                    failed = True
                    logging.error(error)
            else:
                error = form.errors
                failed = True
                logging.error(error)
            
            
            if failed:
                pdt_obj = PayPalPDT()
                pdt_obj.set_flag("Invalid form. %s" % error)
            
            pdt_obj.init(request)
        
            if not failed:
                # the pdt object get's saved during verify
                if pdt_obj.test_ipn:
                    pdt_obj.verify(item_check_callable)
                else:
                    pdt_obj.verify(item_check_callable, test=False)
    else:
        logging.warning("No tx in pdt get request")
 
    context = RequestContext(request, locals())               
    return render_to_response('paypal/standard/pdt.html', context)
