from django.test import TestCase
from django.test.client import Client
from django.core.handlers.wsgi import WSGIRequest
from django.http import QueryDict

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