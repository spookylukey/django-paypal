#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import time
import datetime
import pprint

from django.conf import settings
from django.forms.models import fields_for_model

from paypal.pro.models import PayPalNVP, L


# ### ToDo: Check AVS / CVV2 responses to look for fraudz.
# ### flags etc. on PayPalWPP - tie it 
# ### ToDo: Not very DRY yet... factor out common actions from calls into methods.

USER = settings.PAYPAL_WPP_USER 
PASSWORD = settings.PAYPAL_WPP_PASSWORD
SIGNATURE = settings.PAYPAL_WPP_SIGNATURE
VERSION = 54.0
BASE_PARAMS = dict(USER=USER , PWD=PASSWORD, SIGNATURE=SIGNATURE, VERSION=VERSION)

ENDPOINT = "https://api-3t.paypal.com/nvp"
SANBOX_ENDPOINT = "https://api-3t.sandbox.paypal.com/nvp"

NVP_FIELDS = fields_for_model(PayPalNVP).keys()


def paypal_time(time_obj=None):
    """Returns a time suitable for `profilestartdate` or other PayPal time fields."""
    if time_obj is None:
        time_obj = time.gmtime()
    return time.strftime(PayPalNVP.TIMESTAMP_FORMAT, time_obj)
    
def paypaltime2datetime(s):
    """Convert a PayPal time string to a DateTime."""
    return datetime.datetime(*(time.strptime(s, PayPalNVP.TIMESTAMP_FORMAT)[:6]))

class PayPalError(Exception):
    pass

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
        defaults = {"method": "DoDirectPayment", "paymentaction": "Sale"}
        required = L("creditcardtype acct expdate cvv2 ipaddress firstname lastname street city state countrycode zip amt")
        nvp_obj = self._fetch(params, required, defaults)
        if nvp_obj.flag:
            return False
        else:
            return True

    def setExpressCheckout(self, params):
        """
        Initiates an Express Checkout transaction. 
        Optionally, the SetExpressCheckout API operation can set up billing agreements for
        reference transactions and recurring payments.         
        
        """
        if self._is_recurring(params):
            params = self._recurring_setExpressCheckout_adapter(params)

        defaults = {"method": "SetExpressCheckout", "noshipping": 1}
        required = L("returnurl cancelurl amt")
        # We'll need to use the token to continue.
        return self._fetch(params, required, defaults)

    def doExpressCheckoutPayment(self, params):
        """
        Check the dude out:
        
        """
        defaults = {"method": "DoExpressCheckoutPayment", "paymentaction": "Sale"}
        required =L("returnurl cancelurl amt token payerid")
        nvp_obj = self._fetch(params, required, defaults)
        if nvp_obj.flag:
            return False
        else:
            return True
        
    def createRecurringPaymentsProfile(self, params, direct=False):
        """
        Fields explained in views.
        
        """
        defaults = {"method": "CreateRecurringPaymentsProfile"}
        required = L("profilestartdate billingperiod billingfrequency amt")

        # Direct payments require CC data
        if direct:
            required + L("creditcardtype acct expdate firstname lastname")
        else:
            required + L("token payerid")

        nvp_obj = self._fetch(params, required, defaults)
        
        # Flag if profile_type != ActiveProfile
        if nvp_obj.flag:
            return False
        else:
            return True

    def getExpressCheckoutDetails(self, params):
        raise NotImplementedError

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

    def _is_recurring(self, params):
        if 'billingfrequency' in params:
            return True
        else:
            return False

    def _recurring_setExpressCheckout_adapter(self, params):
        # ### ToDo: The interface to SEC for recurring payments is different than ECP.
        # ### Right now we'll just adapter the keys to what we need.
        params['l_billingtype0'] = "RecurringPayments"
        params['l_billingagreementdescription0'] = params['desc']

        REMOVE = L("billingfrequency billingperiod profilestartdate desc")
        for k in params.keys():
            if k in REMOVE:
                del params[k]
                
        return params

    def _fetch(self, params, required, defaults):
        """
        Make the NVP request and store the response.
        
        """
        # ### This function just sucks.
        
        defaults.update(params)
        pp_params = self._check_and_update_params(required, defaults)        
        pp_string = self.signature + urllib.urlencode(pp_params)
        response = urllib.urlopen(self.endpoint, pp_string).read()
        response_params = self._parse_response(response)
        
        print 'Request:'
        pprint.pprint(defaults)
        print '\nResponse:'
        pprint.pprint(response_params)

        # Put fields from NVP into everything so we can pass it to `create`.
        everything = {}
        def into_everything(d):
            for k, v in d.iteritems():
                if k in NVP_FIELDS:
                    everything[k] = v
        
        into_everything(defaults)
        into_everything(response_params)        

        if 'timestamp' in everything:
            everything['timestamp'] = paypaltime2datetime(everything['timestamp'])

        # Record this NVP.
        nvp_obj = PayPalNVP(**everything)
        nvp_obj.init(self.request, params, response_params)
        nvp_obj.save()
        return nvp_obj

    def _check_and_update_params(self, required, params):
        for r in required:
            if r not in params:
                raise PayPalError("Missing required param: %s" % r)    

        # Upper case all the parameters for PayPal.
        return (dict((k.upper(), v) for k, v in params.iteritems()))
        
    def _parse_response(self, response):
        response_tokens = {}
        for kv in response.split('&'):
            key, value = kv.split("=")
            response_tokens[key.lower()] = urllib.unquote(value)
        return response_tokens