#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST

from paypal.standard.forms import *
from paypal.standard.models import PayPalIPN
from models import POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT
from urllib import unquote_plus
import urllib2
import logging

log = logging.getLogger('paypal')

# PayPal IPN Simulator:
# https://developer.paypal.com/cgi-bin/devscr?cmd=_ipn-link-session

@require_POST
def ipn(request, item_check_callable=None):
    """
    PayPal IPN endpoint (notify_url).
    Used by both PayPal Payments Pro and Payments Standard to confirm transactions.
    
    """
    form = PayPalIPNForm(request.POST)
    failed = False    
    if form.is_valid():
        try:
            ipn_obj = form.save(commit=False)
        except Exception, e:
            error = repr(e)
            failed = True
    else:
        error = form.errors
        failed = True
        
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

    ipn_obj.save()
    return HttpResponse("OKAY")


def pdt(request):
    """
    Payment data transfer implementation
    https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/howto_html_paymentdatatransfer
    """    

    if not settings.PAYPAL_IDENTITY_TOKEN:
        raise Exception("You must set settings.PAYPAL_IDENTITY_TOKEN in settings.py, you can get this token by enabling PDT in your paypal business account")
    
    transaction_status = ''        
    tx = request.GET.get('tx', '')    
    
    postback_dict={}    
    postback_dict["cmd"]="_notify-synch"
    postback_dict["at"]=settings.PAYPAL_IDENTITY_TOKEN    
    postback_dict["tx"]=tx    
    postback_params=urlencode(postback_dict)
    
    PP_URL = POSTBACK_ENDPOINT
    if settings.DEBUG:
        PP_URL = SANDBOX_ENDPOINT
    
    req = urllib2.Request(PP_URL)
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    fo = urllib2.urlopen(PP_URL, postback_params)
    paypal_response = fo.read()
    fo.close()
    paypal_response_list = paypal_response.split('\n')

    paypal_response_dict = {}
    i = 0
    for paypal_line in paypal_response_list:
        unquoted_paypal_line = unquote_plus(paypal_line)        
        if i == 0:
            transaction_status = unquoted_paypal_line.strip()
        else:
            if transaction_status == 'SUCCESS':
                try:
                    [k, v] = unquoted_paypal_line.split('=')
                    paypal_response_dict[k.strip()]=v.strip()
                except ValueError, e:
                    log.error("comfirm_pay_pal error, %s, st=%s"%(e, unquoted_paypal_line))
            else:
                log.error('transaction_status = %s'%transaction_status)
        i = i + 1  
        
    payment_status = ''    
            
    return render_to_response('paypal/standard/pdt.html', {'tx': tx, 
                             'paypal_response_dict': paypal_response_dict, 'transaction_status': transaction_status, 'payment_status': payment_status})