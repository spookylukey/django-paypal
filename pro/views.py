#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

from paypal.pro.forms import PaymentForm, ConfirmForm
from paypal.pro.models import PayPalPaymentInfo
from paypal.pro.helpers import PayPalWPP

# Edit IPN URL:
# https://www.sandbox.paypal.com/us/cgi-bin/webscr?cmd=_profile-ipn-notify

EXPRESS_ENDPOINT = "https://www.paypal.com/webscr?cmd=_express-checkout&%s"
SANDBOX_EXPRESS_ENDPOINT = "https://www.sandbox.paypal.com/webscr?cmd=_express-checkout&%s"
 
RETURN_URL = "http://216.19.180.83:8000/pro/"
CANCEL_URL = "http://216.19.180.83:8000/pro/"
SUCCESS_URL = "http://216.19.180.83:8000/success/" 

class PayPalPro(object):
    """
    This class-based view takes care of Pay Pal Website Payments Pro. It's a monster.
    PayPalPro has two flows - the checkout on your website and checkout on PayPal...

    `item` is a dictionary that holds information about the item.
    
    For single item purchase:
    
        Required Keys:
            * amt: Float amount of the item.
        
        Optional Keys:
            * custom:
            * invnum: Unique ID that identifies this transaction.
    
    For recurring billing:
    
        Required Keys:
          * amt: Float amount for each billing cycle.
          * billingperiod: String unit of measure for the billing cycle (Day|Week|SemiMonth|Month|Year)
          * billingfrequency: Integer number of periods that make up a cycle.
          * profilestartdate: The date to begin billing. "2008-08-05T17:00:00Z" UTC/GMT
          * desc: Description of what you're billing for.
          
        Optional Keys:
          * trialbillingperiod: String unit of measure for trial cycle (Day|Week|SemiMonth|Month|Year)
          * trialbillingfrequency: Integer # of periods in a cycle.
          * trialamt: Float amount to bill for the trial period.
          * trialtotalbillingcycles: Integer # of cycles for the trial payment period.
          * failedinitamtaction: set to continue on failure (ContinueOnFailure / CancelOnFailure)
          * maxfailedpayments: number of payments before profile is suspended.
          * autobilloutamt: automatically bill outstanding amount.
          * subscribername: Full name of the person who paid.
          * profilereference: Unique reference or invoice number.
          * taxamt: How much tax.
          * initamt: Initial non-recurring payment due upon creation.
          * currencycode: defaults to USD
          * + a bunch of shipping fields
        
        `payment_form_cls` is the form class that will be used to display the payment form.
        It should inherit from `paypal.pro.forms.PaymentForm` if you're adding more.
        
        `payment_template` is the template used to ask the dude for monies. To comply with
        PayPal regs. it must include a link to PayPal Express Checkout.
        
        `confirm_form_cls` is the form class that will be used to display the confirmation form.
        It should inherit from `paypal.pro.forms.ConfirmForm`. It is only used in the Express flow.
        
        `success_url` & `fail_url` are URLs to be redirected to when the payment is comlete or fails.
        
        If `test` is True the transaction will take place in the PayPal sandbox.
    
    """

    # ### Todo: Work item / recurring data into one parameter?
    def __init__(self, item=None, 
                 payment_form_cls=PaymentForm, 
                 payment_template="pro/payment.html",
                 confirm_form_cls=ConfirmForm, 
                 confirm_template="pro/confirm.html",
                 success_url="?success", fail_url=None, test=True):
        self.item = item
        self.payment_form_cls = payment_form_cls
        self.payment_template = payment_template
        self.confirm_form_cls = confirm_form_cls
        self.confirm_template = confirm_template
        self.success_url = success_url
        self.fail_url = fail_url
        if test:
            self.express_endpoint = SANDBOX_EXPRESS_ENDPOINT
        else:
            self.express_endpoint = EXPRESS_ENDPOINT

    def __call__(self, request):
        """
        Spin off and call the appropriate thing..
        
        """
        self.request = request
        if request.method == "GET":
            if 'express' in request.GET:
                return self.redirect_to_express()
            elif 'token' in request.GET and 'PayerID' in request.GET:
                return self.render_confirm_form()
            else:
                return self.render_payment_form() 
        else:
            if 'token' in request.POST and 'PayerID' in request.POST:
                return self.validate_confirm_form()
            else:
                return self.validate_payment_form()

    def render_payment_form(self, context=None):
        """
        Display the Payment form for entering the monies.
        
        """
        context = context or {}
        context['form'] = self.payment_form_cls()
        return render_to_response(self.payment_template, context, RequestContext(self.request))

    def validate_payment_form(self, context=None):
        """
        Try a Direct Payment and if the form validates ask PayPal for the money.
        
        """
        failed = False  # Did the form pass validation?
        success = False  # Was processing successful?
        form = self.payment_form_cls(self.request.POST)
        
        if form.is_valid():
            payment_obj = form.save(commit=False)
        else:
            failed = True
            payment_obj = PayPalPaymentInfo()
            payment_obj.set_flag("Bad form data: %s" % form.errors)    

        payment_obj.init(self.request)
        if not failed:
            success = payment_obj.process(self.request, self.item)
        payment_obj.save()
        if success:
            return HttpResponseRedirect(self.success_url)
        elif self.fail_url is not None:
            return HttpResponseRedirect(self.fail_url)

        # Failed, render the payment form w/ errors.
        context = context or {}
        context['form'] = form
        context['errors'] = "Please correct the errors below and try again."
        return render_to_response(self.payment_template, context, RequestContext(self.request))

    def redirect_to_express(self):
        """
        First express flow step.
        Redirect to PayPal with the data in tow.
        
        """
        wpp = PayPalWPP()
        response = wpp.setExpressCheckout(self.item)
        if response.get('ACK') == 'Success' and 'TOKEN' in response:
            pp_params = dict(token=response['TOKEN'], 
                             AMT=self.item['amt'], 
                             RETURNURL=self.item['returnurl'], 
                             CANCELURL=self.item['cancelurl'])
            pp_url = SANDBOX_EXPRESS_ENDPOINT % urllib.urlencode(pp_params)
            return HttpResponseRedirect(pp_url)
        else:
            context = {'errors':'There was a problem contacting PayPal. Please try again later.'}
            return self.render_payment_form(context)

    def render_confirm_form(self, context=None):
        """
        Second express flow step.
        Show the confirmation form to get the guy to click I approve.
        
        """
        context = context or {}
        initial = {'token': self.request.GET['token'], 'PayerID': self.request.GET['PayerID']}
        context['form'] = self.confirm_form_cls(initial=initial)
        return render_to_response(self.confirm_template, context, RequestContext(self.request))

    def validate_confirm_form(self):
        """
        Final express flow step.
        User has pressed the confirm button and now we send it off to PayPal.
        
        """
        wpp = PayPalWPP()
        pp_data = dict(token=self.request.POST['token'], payerid=self.request.POST['PayerID'])
        self.item_data.update(pp_data)
        response = wpp.doExpressCheckoutPayment(self.item)
        if response.get('ACK') == 'Success':
            return HttpResponseRedirect(self.success_url)
        else:
            context = {'errors':'There was a problem processing the payment. Please check your information and try again.'}
            return self.render_payment_form(context)
            

    


item = dict(custom='cust', invnum='inve4', amt=10.0, returnurl=RETURN_URL, cancelurl=CANCEL_URL)
pro = PayPalPro(item=item)


# ### Todo: Rework `payment` parameters. and the name.
# ### ToDo: Could `express` be a class based view to be a little less confusing?

# def paypalpro(request, item_data=None, reccuring_data=None, template="pro/payment.html", context=None, success_url="", fail_url=None):
#     context = context or {}
# 
#         
#     # item_data = item_data or dict(custom='cust', invnum='inve', amt=10.0)
#     reccuring_data = dict(desc="Mobify.Me Premium", billingperiod="Month", billingfrequency=1, amt=10.0, profilestartdate='2009-02-02T19:11:01Z')
# 
# 
#     if request.method == "POST":
#         failed = False  # Did the form pass validation?
#         success = False  # Was processing successful?
#         form = PaymentForm(request.POST)
# 
#         if form.is_valid():
#             payment_obj = form.save(commit=False)
#         else:
#             failed = True
#             payment_obj = PayPalPaymentInfo()
#             payment_obj.set_flag("Bad form data: %s" % form.errors)
# 
#         # If the payment has not failed, try processing it.
#         payment_obj.init(request)
#         if not failed:
#             success = payment_obj.process(request, item_data, reccuring_data)
#         payment_obj.save()        
# 
#         if success:
#             return HttpResponseRedirect(success_url)
#         elif fail_url is not None:
#             return HttpResponseRedirect(fail_url)
# 
#     else:
#         form = PaymentForm(initial=item_data)
#         
#     context['form'] = form
#     return render_to_response(template, context)


# ### ToDo: return_url should be a reverse to yourself.
# ### ToDo: Since by PP def. this has to be coupled to `payment` can we put them together?

# def express(request, template="pro/confirm.html", 
#             return_url="http://216.19.180.83:8000/express/", cancel_url="http://216.19.180.83:8000/cancel/", 
#             success_url="http://216.19.180.83:8000/success_url/"):
#     """
#     Express checkout flow.
# 
#     """
#     
#     
#     # item_params should be passed in.
#     params = dict(custom='cust', invnum='inve2', amt=10.0, returnurl=return_url, cancelurl=cancel_url)
#     
#     # Pressed confirm - go ahead an bill.
#     if request.method == "POST":
#         wpp = PayPalWPP()
#         params.update(dict(token=request.POST['token'], payerid=request.POST['payerid']))
#         response = wpp.doExpressCheckoutPayment(params)
#         return HttpResponseRedirect(success_url)
#     
#     
#     
#     # Starting the Express flow - redirect to PayPal.
#     if 'token' not in request.GET and 'PayerID' not in request.GET:    
#         wpp = PayPalWPP()
#         response = wpp.setExpressCheckout(params)
#         if 'TOKEN' in response:
#             pp_params = dict(token=response['TOKEN'], AMT=params['amt'], RETURNURL=params['returnurl'], CANCELURL=params['cancelurl'])
#             pp_url = SANDBOX_EXPRESS_ENDPOINT % urllib.urlencode(pp_params)
#             return HttpResponseRedirect(pp_url)
# 
#     # Payment approved - ready to confirm.
#     if 'token' in request.GET and 'PayerID' in request.GET:
#         token = request.GET['token']
#         payerid = request.GET['PayerID']
#         # Ask the dude to hit the confirm button!
#         return render_to_response(template, {'token': token, 'payerid': payerid})
# 
#         
#         
#     def doExpressCheckoutPayment(self, params):
#         
#         defaults = dict(METHOD="DoExpressCheckoutPayment", PAYMENTACTION="Sale")
#         required ="returnurl cancelurl amt token payerid".split()
#         print pp_params
#         return self._fetch(pp_params)