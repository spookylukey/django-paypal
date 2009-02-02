#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib

from django.conf import settings


USER = settings.PAYPAL_WPP_USER 
PASSWORD = settings.PAYPAL_WPP_PASSWORD
SIGNATURE = settings.PAYPAL_WPP_SIGNATURE
VERSION = "50.0"
BASE_PARAMS = dict(USER=USER , PWD=PASSWORD, SIGNATURE=SIGNATURE, VERSION=VERSION)

ENDPOINT = "https://api-3t.paypal.com/nvp"
SANBOX_ENDPOINT = "https://api-3t.sandbox.paypal.com/nvp"


class PayPalError(Exception):
    pass
    
class PayPalWPP(object):
    """
    PayPal Website Payments Pro.
    https://cms.paypal.com/cms_content/US/en_US/files/developer/PP_WPP_IntegrationGuide.pdf
    """
    def __init__(self, params=BASE_PARAMS, test=True):
        """
        Required - USER / PWD / SIGNATURE / VERSION
        """
        if test:
            self.endpoint = SANBOX_ENDPOINT
        else:
            self.endpoint = ENDPOINT
        self.signature_values = params
        self.signature = urllib.urlencode(self.signature_values) + "&"

    def doDirectPayment(self, params):
        """
        Do direct payment. Woot, this is where we take the money from the guy.        

        https://www.paypal.com/en_US/ebook/PP_NVPAPI_DeveloperGuide/directpayment.html
        
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
        
        {'ORDERTIME': '2009-02-02T16:48:41Z', 'ACK': 'Success', 'TIMESTAMP': '2009-02-02T16:48:43Z', 'CURRENCYCODE': 'USD', 'PAYMENTSTATUS': 'Completed', 'PENDINGREASON': 'None', 'PAYMENTTYPE': 'instant', 'TOKEN': 'EC-4FD207377L4986412', 'VERSION': '50.0', 'BUILD': '801690', 'TAXAMT': '0.00', 'FEEAMT': '0.59', 'REASONCODE': 'None', 'TRANSACTIONID': '1WF99451L2124605U', 'AMT': '10.00', 'CORRELATIONID': '46bcc23d964ad', 'TRANSACTIONTYPE': 'expresscheckout'}
        
        """
        defaults = dict(METHOD="DoExpressCheckoutPayment", PAYMENTACTION="Sale")
        required ="returnurl cancelurl amt token payerid".split()
        pp_params = self._check_and_update_params(params, required, defaults)
        print pp_params
        return self._fetch(pp_params)
        
    def createRecurringPaymentsProfile(self, params):
        """
        profilestartdate - date when the billing profile begins
        billingperiod - day/week/semimonth/month/year
        billingfrequency - number of billing periods in one billing cycle
        amt - amount of each cycle    

        # 
        TRIALBILLINGPERIOD - 
        TRIALBILLINGFREQUENCY -
        TRIALAMT -
        TRIALTOTALBILLINGCYCLES -
        
        # Initial Payment
        INITAMT
        FAILEDINITAMTACTION
        
        MAXFAILEDPAYMENTS
        
        AUTOBILLOUTAMT
        
        """
    
    
        require = "creditcardtype acct expdate firstname lastname profilestartdate billingperiod billingfrequency amt"

    def getRecurringPaymentsProfileDetails(self, params):
        raise NotImplementedError

    def updateRecurringPaymentsProfile(self, params):
        raise NotImplementedError
    
    def billOutstandingAmount(self, params):
        raise NotImplementedError
        
    def manangeRecurringPaymentsProfileStatus(self, params):
        raise NotImplementedError
        
    def RefundTransaction(self, params):
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
        return tok
        
    def _parse_response(self, response):
        response_tokens = {}
        for kv in response.split('&'):
            key, value = kv.split("=")
            response_tokens[key] = urllib.unquote(value)
        return response_tokens
 




"""
SUCCESS

Success

SuccessWithWarning 

ACK=Success&TIMESTAMP=date/timeOfResponse
&CORRELATIONID=debuggingToken&VERSION=...
&BUILD=buildNumber 
"""

"""
ERROR:
Failure|FailureWithWarning|Warning 

ACK=Error&TIMESTAMP=date/timeOfResponse&
CORRELATIONID=debuggingToken&VERSION=VersionNo&
BUILD=buildNumber&L_ERRORCODE0=errorCode&
L_SHORTMESSAGE0=shortMessage&
L_LONGMESSAGE0=longMessage&
L_SEVERITYCODE0=severityCode 


"""


# 
# 
# 
# 
#     

#     

#         
#     def GetTransactionDetails(self, tx_id):
#         params = {
#             'METHOD' : "GetTransactionDetails", 
#             'TRANSACTIONID' : tx_id,
#         }
#         params_string = self.signature + urllib.urlencode(params)
#         response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
#         response_tokens = {}
#         for token in response.split('&'):
#             response_tokens[token.split("=")[0]] = token.split("=")[1]
#         for key in response_tokens.keys():
#                 response_tokens[key] = urllib.unquote(response_tokens[key])
#         return response_tokens
#                 
#     def MassPay(self, email, amt, note, email_subject):
#         unique_id = str(md5.new(str(datetime.datetime.now())).hexdigest())
#         params = {
#             'METHOD' : "MassPay",
#             'RECEIVERTYPE' : "EmailAddress",
#             'L_AMT0' : amt,
#             'CURRENCYCODE' : 'USD',
#             'L_EMAIL0' : email,
#             'L_UNIQUE0' : unique_id,
#             'L_NOTE0' : note,
#             'EMAILSUBJECT': email_subject,
#         }
#         params_string = self.signature + urllib.urlencode(params)
#         response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
#         response_tokens = {}
#         for token in response.split('&'):
#             response_tokens[token.split("=")[0]] = token.split("=")[1]
#         for key in response_tokens.keys():
#                 response_tokens[key] = urllib.unquote(response_tokens[key])
#         response_tokens['unique_id'] = unique_id
#         return response_tokens
#                 
#     
#     def CreateRecurringPaymentsProfile(self, token, startdate, desc, period, freq, amt):
#         params = {
#             'METHOD': 'CreateRecurringPaymentsProfile',
#             'PROFILESTARTDATE': startdate,
#             'DESC':desc,
#             'BILLINGPERIOD':period,
#             'BILLINGFREQUENCY':freq,
#             'AMT':amt,
#             'TOKEN':token,
#             'CURRENCYCODE':'USD',
#         }
#         params_string = self.signature + urllib.urlencode(params)
#         response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
#         response_dict = parse_qs(response)
#         return response_dict
