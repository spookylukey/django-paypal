#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.forms import ValidationError
from django.http import QueryDict
from django.test import TestCase
from django.test.client import Client

from paypal.pro.fields import CreditCardField
from paypal.pro.helpers import PayPalWPP, PayPalError


class RequestFactory(Client):
    # Used to generate request objects.
    def request(self, **request):
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)

RF = RequestFactory()
REQUEST = RF.get("/pay/", REMOTE_ADDR="127.0.0.1:8000")


class DummyPayPalWPP(PayPalWPP):
    pass
#     """Dummy class for testing PayPalWPP."""
#     responses = {
#         # @@@ Need some reals data here.
#         "DoDirectPayment": """ack=Success&timestamp=2009-03-12T23%3A52%3A33Z&l_severitycode0=Error&l_shortmessage0=Security+error&l_longmessage0=Security+header+is+not+valid&version=54.0&build=854529&l_errorcode0=&correlationid=""",
#     }
# 
#     def _request(self, data):
#         return self.responses["DoDirectPayment"]


class CreditCardFieldTest(TestCase):
    def testCreditCardField(self):
        field = CreditCardField()
        field.clean('4797503429879309')
        self.assertEquals(field.card_type, "Visa")
        self.assertRaises(ValidationError, CreditCardField().clean, '1234567890123455')

        
class PayPalWPPTest(TestCase):
    def setUp(self):
    
        # Avoding blasting real requests at PayPal.
        self.old_debug = settings.DEBUG
        settings.DEBUG = True
            
        self.item = {
            'amt': '9.95',
            'inv': 'inv',
            'custom': 'custom',
            'next': 'http://www.example.com/next/',
            'returnurl': 'http://www.example.com/pay/'
        }                    
        self.wpp = DummyPayPalWPP(REQUEST)
        
    def tearDown(self):
        settings.DEBUG = self.old_debug

    def test_doDirectPayment_missing_params(self):
        data = {'firstname': 'Chewbacca'}
        self.assertRaises(PayPalError, self.wpp.doDirectPayment, data)

    def test_doDirectPayment_valid(self):
        data = {
            'firstname': 'Brave',
            'lastname': 'Star',
            'street': '1 Main St',
            'city': u'San Jos\xe9',
            'state': 'CA',
            'countrycode': 'US',
            'zip': '95131',
            'expdate': '012019',
            'cvv2': '037',
            'acct': '4797503429879309',
            'creditcardtype': 'visa',
            'ipaddress': '10.0.1.199',}
        data.update(self.item)
        self.assertTrue(self.wpp.doDirectPayment(data))
        
    def test_doDirectPayment_invalid(self):
        data = {
            'firstname': 'Epic',
            'lastname': 'Fail',
            'street': '100 Georgia St',
            'city': 'Vancouver',
            'state': 'BC',
            'countrycode': 'CA',
            'zip': 'V6V 1V1',
            'expdate': '012019',
            'cvv2': '999',
            'acct': '1234567890',
            'creditcardtype': 'visa',
            'ipaddress': '10.0.1.199',}
        data.update(self.item)
        self.assertFalse(self.wpp.doDirectPayment(data))

    def testSetExpressCheckout(self):
        ""
        pass

### SetExpressCheckout
# PayPal Request:
# {'amt': '10.00',
#  'cancelurl': 'http://xxx.xxx.xxx.xxx/deploy/480/upgrade/?upgrade=cname',
#  'custom': u'website_id=480&cname=1',
#  'inv': u'website-480-cname',
#  'method': 'SetExpressCheckout',
#  'next': 'http://xxx.xxx.xxx.xxx/deploy/480/upgrade/?upgrade=cname',
#  'noshipping': 1,
#  'returnurl': 'http://xxx.xxx.xxx.xxx/deploy/480/upgrade/?upgrade=cname'}
# 
# PayPal Response:
# {'ack': 'Success',
#  'build': '848077',
#  'correlationid': '44977a68d0bea',
#  'timestamp': '2009-03-04T20:55:07Z',
#  'token': 'EC-6HW17184NE0084127',
#  'version': '54.0'}

### DoExpressCheckoutPayment
# PayPal Request:
# {'amt': '10.00',
#  'cancelurl': u'http://xxx.xxx.xxx.xxx/deploy/480/upgrade/?upgrade=cname',
#  'custom': u'website_id=480&cname=1',
#  'inv': u'website-480-cname',
#  'method': 'DoExpressCheckoutPayment',
#  'next': u'http://xxx.xxx.xxx.xxx/deploy/480/upgrade/?upgrade=cname',
#  'payerid': u'BN5JZ2V7MLEV4',
#  'paymentaction': 'Sale',
#  'returnurl': u'http://xxx.xxx.xxx.xxx/deploy/480/upgrade/?upgrade=cname',
#  'token': u'EC-6HW17184NE0084127'}
# 
# PayPal Response:
# {'ack': 'Success',
#  'amt': '10.00',
#  'build': '848077',
#  'correlationid': '375f4773c3d34',
#  'currencycode': 'USD',
#  'feeamt': '0.59',
#  'ordertime': '2009-03-04T20:56:08Z',
#  'paymentstatus': 'Completed',
#  'paymenttype': 'instant',
#  'pendingreason': 'None',
#  'reasoncode': 'None',
#  'taxamt': '0.00',
#  'timestamp': '2009-03-04T20:56:09Z',
#  'token': 'EC-6HW17184NE0084127',
#  'transactionid': '3TG42202A7335864V',
#  'transactiontype': 'expresscheckout',
#  'version': '54.0'}

"""
PayPal Request:
{'acct': '1234567890',
 'amt': '9.95',
 'city': 'Vancouver',
 'countrycode': 'CA',
 'creditcardtype': 'visa',
 'custom': 'custom',
 'cvv2': '999',
 'expdate': '012019',
 'firstname': 'Epic',
 'inv': 'inv',
 'ipaddress': '10.0.1.199',
 'lastname': 'Fail',
 'method': 'DoDirectPayment',
 'next': 'http://www.example.com/next/',
 'paymentaction': 'Sale',
 'returnurl': 'http://www.example.com/pay/',
 'state': 'BC',
 'street': '100 Georgia St',
 'zip': 'V6V 1V1'}
 


PayPal Response:
{'ack': 'Failure',
 'amt': '9.95',
 'build': '962735',
 'correlationid': '6c7470a26f50',
 'currencycode': 'USD',
 'l_errorcode0': '10527',
 'l_longmessage0': 'This transaction cannot be processed. Please enter a valid credit card number and type.',
 'l_severitycode0': 'Error',
 'l_shortmessage0': 'Invalid Data',
 'timestamp': '2009-07-14T16:25:14Z',
 'version': '54.0'}



PayPal Request:
{'acct': '4797503429879309',
 'amt': '9.95',
 'city': u'San Jos\xe9',
 'countrycode': 'US',
 'creditcardtype': 'visa',
 'custom': 'custom',
 'cvv2': '037',
 'expdate': '012019',
 'firstname': 'Brave',
 'inv': 'inv',
 'ipaddress': '10.0.1.199',
 'lastname': 'Star',
 'method': 'DoDirectPayment',
 'next': 'http://www.example.com/next/',
 'paymentaction': 'Sale',
 'returnurl': 'http://www.example.com/pay/',
 'state': 'CA',
 'street': '1 Main St',
 'zip': '95131'}

PayPal Response:
{'ack': 'Success',
 'amt': '9.95',
 'avscode': 'X',
 'build': '962735',
 'correlationid': '36c8179352160',
 'currencycode': 'USD',
 'cvv2match': 'M',
 'timestamp': '2009-07-14T16:25:22Z',
 'transactionid': '4NC00018J73871820',
 'version': '54.0'}

"""