from django.test import TestCase
from django.test.client import Client
from django.core.handlers.wsgi import WSGIRequest
from django.http import QueryDict
from django.forms import ValidationError

from paypal.pro.fields import CreditCardField
from paypal.pro.helpers import PayPalWPP


class RequestFactory(Client):
    # This generates fake requests to pass to WPP.
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


# class DummyPayPalWPP(PayPalWPP):
#     """
#     Dummy class for testing PayPalWPP.
#     
#     """
#     def _fetch(self, data):
#         params = QueryDict(data)
#         return DummyResponses[params["METHOD"]]
        # Fake PayPal responses
#         self.responses = {
#             "DoDirectPayment": "Dodirect pay!!!",}


class CreditCardFieldTest(TestCase):
    def testCreditCardField(self):
        field = CreditCardField()
        field.clean('4797503429879309')
        self.assertEquals(field.card_type, "Visa")
        self.assertRaises(ValidationError, CreditCardField().clean, '1234567890123455')

        
class PayPalWPPTestCase(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.request = self.rf.get("/pay/", REMOTE_ADDR="10.0.1.199")
        self.item = {
            'amt': '9.95',
            'inv': 'inv',
            'custom': 'custom',
            'next': 'http://www.example.com/next/',
            'returnurl': 'http://www.example.com/pay/',}                    
        self.wpp = DummyPayPalWPP(self.request)

    def testDoDirectPayment(self):
        ""
        # Partial data should throw exception.
        partial_data = {'firstname': 'Chewbacca'}
        self.assertRaises(self.wpp.doDirectPayment(partial_data))

        # Full data should return True!
        full_data = {
            'firstname': 'Brave',
            'lastname': 'Star',
            'street': '1 Main St',
            'city': 'San Jose',
            'state': 'CA',
            'countrycode': 'US',
            'zip': '95131',
            'expdate': '012019',
            'cvv2': '037',
            'acct': '4797503429879309',
            'creditcardtype': 'visa',
            'ipaddress': '10.0.1.199',}
        full_data.update(self.item)        
        self.assertTrue(self.wpp.doDirectPayment(full_data))

        # Failure data should return False!
        fail_data = {
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
        fail_data.update(self.item)
        self.assertFalse(self.wpp.doDirectPayment(fail_data))

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