#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

from paypal.pro.forms import PaymentForm, ConfirmForm
from paypal.pro.models import PayPalNVP
from paypal.pro.helpers import PayPalWPP
from paypal.pro.signals import payment_was_successful, payment_was_flagged


# PayPal Edit IPN URL:
# https://www.sandbox.paypal.com/us/cgi-bin/webscr?cmd=_profile-ipn-notify

EXPRESS_ENDPOINT = "https://www.paypal.com/webscr?cmd=_express-checkout&%s"
SANDBOX_EXPRESS_ENDPOINT = "https://www.sandbox.paypal.com/webscr?cmd=_express-checkout&%s"

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
    def __init__(self, item=None, 
                 payment_form_cls=PaymentForm, 
                 payment_template="pro/payment.html",
                 confirm_form_cls=ConfirmForm, 
                 confirm_template="pro/confirm.html",
                 success_url="?success", fail_url=None, test=True, context=None):
        self.item = item
        self.is_recurring = False
        if 'billingperiod' in item:
            self.is_recurring = True
            print self.is_recurring
        # ### Could we set these based off success_url / fail_url?
        # self.item.setdefault('returnurl', )
        # self.item.setdefault('cancelurl', )
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
        self.context = context or {}

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

    def render_payment_form(self):
        """
        Display the Payment form for entering the monies.
        
        """
        self.context['form'] = self.payment_form_cls()
        return render_to_response(self.payment_template, self.context, RequestContext(self.request))

    def validate_payment_form(self):
        """
        Try a Direct Payment and if the form validates ask PayPal for the money.
        
        """
        form = self.payment_form_cls(self.request.POST)        
        if form.is_valid():
            success = form.process(self.request, self.item)
            if success:
                payment_was_successful.send(sender=self.item)
                return HttpResponseRedirect(self.success_url)
            else:
                self.context['errors'] = "There was an error processing your payment. Check your information and try again."

        # Failed, render the payment form w/ errors.
        self.context['form'] = form
        self.context.setdefault('errors', 'Please correct the errors below and try again.')
        return render_to_response(self.payment_template, self.context, RequestContext(self.request))

    def redirect_to_express(self):
        """
        First express flow step.
        Redirect to PayPal with the data in tow.
        
        """
        wpp = PayPalWPP(self.request)
        nvp_obj = wpp.setExpressCheckout(self.item)
        if not nvp_obj.flag:
            pp_params = dict(token=nvp_obj.token, 
                             AMT=self.item['amt'], 
                             RETURNURL=self.item['returnurl'], 
                             CANCELURL=self.item['cancelurl'])
            pp_url = SANDBOX_EXPRESS_ENDPOINT % urllib.urlencode(pp_params)
            return HttpResponseRedirect(pp_url)
        else:
            self.context = {'errors':'There was a problem contacting PayPal. Please try again later.'}
            return self.render_payment_form(self.context)

    def render_confirm_form(self):
        """
        Second express flow step.
        Show the confirmation form to get the guy to click I approve.
        
        """
        initial = {'token': self.request.GET['token'], 'PayerID': self.request.GET['PayerID']}
        self.context['form'] = self.confirm_form_cls(initial=initial)
        return render_to_response(self.confirm_template, self.context, RequestContext(self.request))

    def validate_confirm_form(self):
        """
        Final express flow step.
        User has pressed the confirm button and now we send it off to PayPal.
        
        """
        wpp = PayPalWPP(self.request)
        pp_data = dict(token=self.request.POST['token'], payerid=self.request.POST['PayerID'])
        self.item.update(pp_data)
        
        if self.is_recurring:
            success = wpp.createRecurringPaymentsProfile(self.item)
        else:
            success = wpp.doExpressCheckoutPayment(self.item)

        if success:
            payment_was_successful.send(sender=self.item)
            return HttpResponseRedirect(self.success_url)
        else:
            self.context = {'errors':'There was a problem processing the payment. Please check your information and try again.'}
            return self.render_payment_form(self.context)