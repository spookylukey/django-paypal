#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

from paypal.pro.forms import PaymentForm
from paypal.pro.models import PayPalPaymentInfo
from paypal.pro.helpers import PayPalWPP

# Edit IPN URL:
# https://www.sandbox.paypal.com/us/cgi-bin/webscr?cmd=_profile-ipn-notify

SANDBOX_EXPRESS_ENDPOINT = "https://www.sandbox.paypal.com/webscr?cmd=_express-checkout&%s"


# ### Todo: Rework `payment` parameters. and the name.
# ### ToDo: Could `express` be a class based view to be a little less confusing?

def payment(request, item_data=None, template="pro/payment.html", context=None, success_url="", fail_url=None):
    context = context or {}

    if request.method == "POST":
        failed = False  # Did the form pass validation?
        success = False  # Was processing successful?
        form = PaymentForm(request.POST)

        if form.is_valid():
            payment_obj = form.save(commit=False)
        else:
            failed = True
            payment_obj = PayPalPaymentInfo()
            payment_obj.set_flag("Bad form data: %s" % form.errors)


        # If the payment has not failed, try processing it.
        payment_obj.init(request)
        if not failed:
            item_data = item_data or dict(custom='cust', invnum='inve', amt=10.0)
            success = payment_obj.process(request, item_data)
        payment_obj.save()        

        # Redirect accordingly!
        if success:
            return HttpResponse(success_url)
        elif fail_url is not None:
            return HttpResponse(fail_url)

    else:
        form = PaymentForm(initial=item_data)
        
    context['form'] = form
    return render_to_response(template, context)


# ### ToDo: return_url should be a reverse to yourself.
# ### ToDo: Since by PP def. this has to be coupled to `payment` can we put them together?

def express(request, template="pro/confirm.html", 
            return_url="http://216.19.180.83:8000/express/", cancel_url="http://216.19.180.83:8000/cancel/", 
            success_url="http://216.19.180.83:8000/success_url/"):
    """
    Express checkout flow.

    """
    
    
    # item_params should be passed in.
    params = dict(custom='cust', invnum='inve2', amt=10.0, returnurl=return_url, cancelurl=cancel_url)
    
    # Pressed confirm - go ahead an bill.
    if request.method == "POST":
        wpp = PayPalWPP()
        params.update(dict(token=request.POST['token'], payerid=request.POST['payerid']))
        response = wpp.doExpressCheckoutPayment(params)
        return HttpResponseRedirect(success_url)
    
    
    
    # Starting the Express flow - redirect to PayPal.
    if 'token' not in request.GET and 'PayerID' not in request.GET:    
        wpp = PayPalWPP()
        response = wpp.setExpressCheckout(params)
        if 'TOKEN' in response:
            pp_params = dict(token=response['TOKEN'], AMT=params['amt'], RETURNURL=params['returnurl'], CANCELURL=params['cancelurl'])
            pp_url = SANDBOX_EXPRESS_ENDPOINT % urllib.urlencode(pp_params)
            return HttpResponseRedirect(pp_url)

    # Payment approved - ready to confirm.
    if 'token' in request.GET and 'PayerID' in request.GET:
        token = request.GET['token']
        payerid = request.GET['PayerID']
        # Ask the dude to hit the confirm button!
        return render_to_response(template, {'token': token, 'payerid': payerid})

        
        
#     def doExpressCheckoutPayment(self, params):
#         
#         defaults = dict(METHOD="DoExpressCheckoutPayment", PAYMENTACTION="Sale")
#         required ="returnurl cancelurl amt token payerid".split()
#         print pp_params
#         return self._fetch(pp_params)