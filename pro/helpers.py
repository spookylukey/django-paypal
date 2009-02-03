#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import time

from django.conf import settings

from paypal.pro.models import PayPalNVP

USER = settings.PAYPAL_WPP_USER 
PASSWORD = settings.PAYPAL_WPP_PASSWORD
SIGNATURE = settings.PAYPAL_WPP_SIGNATURE
VERSION = 54.0
BASE_PARAMS = dict(USER=USER , PWD=PASSWORD, SIGNATURE=SIGNATURE, VERSION=VERSION)

ENDPOINT = "https://api-3t.paypal.com/nvp"
SANBOX_ENDPOINT = "https://api-3t.sandbox.paypal.com/nvp"


def paypal_time(time_obj=None):
    """Returns a time suitable for `profilestartdate` or other PayPal time fields."""
    if time_obj is None:
        time_obj = time.gmtime()
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time_obj)


class PayPalError(Exception):
    pass

# ### ToDo: Record all interactions with paypal NVP.

class PayPalWPP(object):
    """
    Wrapper class for the PayPal Website Payments Pro.
    
    Website Payments Pro Integration Guide:
    https://cms.paypal.com/cms_content/US/en_US/files/developer/PP_WPP_IntegrationGuide.pdf

    Name-Value Pair API Developer Guide and Reference:
    https://cms.paypal.com/cms_content/US/en_US/files/developer/PP_NVPAPI_DeveloperGuide.pdf

    """
    def __init__(self, request, params=BASE_PARAMS, test=True):
        """
        Required - USER / PWD / SIGNATURE / VERSION

        """
        self.request = request
        if test:
            self.endpoint = SANBOX_ENDPOINT
        else:
            self.endpoint = ENDPOINT
        self.signature_values = params
        self.signature = urllib.urlencode(self.signature_values) + "&"

    def doDirectPayment(self, params):
        """
        Do direct payment. Woot, this is where we take the money from the guy.        
        
        """
        defaults = dict(METHOD="DoDirectPayment", PAYMENTACTION="Sale")
        required = "creditcardtype acct expdate cvv2 ipaddress firstname lastname street city state countrycode zip amt".split()
        pp_params = self._check_and_update_params(params, required, defaults)
        print pp_params
        return self._fetch(pp_params)

    def setExpressCheckout(self, params):
        """
        Setup an express payment. Token is the important thing.
        
        """
        # custom invnum notifyurl
        defaults = dict(METHOD="SetExpressCheckout", NOSHIPPING=1)
        required = "returnurl cancelurl amt".split()
        pp_params = self._check_and_update_params(params, required, defaults)
        print pp_params
        return self._fetch(pp_params)

    def getExpressCheckoutDetails(self, params):
        """
        From the PayPal docs:
        
        Although you are not required to invoke the GetExpressCheckoutDetails API operation, 
        most Express Checkout implementations take this action to obtain information about the 
        buyer. You invoke the GetExpressCheckoutDetails API operation from the page 
        specified by return URL, which you set in your call to the SetExpressCheckout API. 
        Typically, you invoke this operation as soon as the redirect occurs and use the information in 
        the response to populate your review page.
        
        """
        defaults = dict(METHOD="GetExpressCheckoutDetails")
        required ="returnurl cancelurl token".split()
        pp_params = self._check_and_update_params(params, required, defaults)
        print pp_params
        return self._fetch(pp_params)

    def doExpressCheckoutPayment(self, params):
        """
        Check the dude out:
        
        """
        defaults = dict(METHOD="DoExpressCheckoutPayment", PAYMENTACTION="Sale")
        required ="returnurl cancelurl amt token payerid".split()
        pp_params = self._check_and_update_params(params, required, defaults)
        print pp_params
        return self._fetch(pp_params)
        
    def createRecurringPaymentsProfile(self, params, direct=False):
        """
        Fields explained in views.
        
        Response:
            * profileid: unique id for future reference.
            * status: (ActiveProfile|PendingProfile)
        
        """
        defaults = dict(METHOD="CreateRecurringPaymentsProfile")
        required = "profilestartdate billingperiod billingfrequency amt".split()
        # Direct payments require CC data
        if direct:
            required + "creditcardtype acct expdate firstname lastname".split()
        else:
            required + ["token", "payerid"]

        pp_params = self._check_and_update_params(params, required, defaults)
        print pp_params
        return self._fetch(pp_params)

    def setCustomerBillingAgreement(self, params):
        raise DeprecationWarning

    def getTransactionDetails(self, params):
        raise NotImplementedError

    def massPay(self, params):
        raise NotImplementedError

    def getRecurringPaymentsProfileDetails(self, params):
        raise NotImplementedError

    def updateRecurringPaymentsProfile(self, params):
        raise NotImplementedError
    
    def billOutstandingAmount(self, params):
        raise NotImplementedError
        
    def manangeRecurringPaymentsProfileStatus(self, params):
        raise NotImplementedError
        
    def refundTransaction(self, params):
        raise NotImplementedError

    def _check_and_update_params(self, params, required, defaults):
        for r in required:
            if r not in params:
                raise PayPalError("Missing required param: %s" % r)    

        # Upcase all the keys and put them in with the defaults.
        defaults.update(dict((k.upper(), v) for k, v in params.iteritems()))
        return defaults

    def _fetch(self, params):
        params_string = self.signature + urllib.urlencode(params)
        
        print self.endpoint
        print params_string
        
        response = urllib.urlopen(self.endpoint, params_string).read()
        tok = self._parse_response(response)
        print tok
        
        # Record this NVP.
        nvp_obj = PayPalNVP()
        nvp_obj.init(self.request, params, tok)
        if tok.get('ACK') != 'Success':
            nvp_obj.set_flag(tok.get('L_LONGMESSAGE0'), tok.get('L_ERRORCODE0'))
        nvp_obj.save()        
        
        return tok
        
        # ### ToDo: Return the nvp_obj and the tok so the caller can do post processing.
        # return nvp_obj, tok
        
    def _parse_response(self, response):
        response_tokens = {}
        for kv in response.split('&'):
            key, value = kv.split("=")
            response_tokens[key] = urllib.unquote(value)
        return response_tokens