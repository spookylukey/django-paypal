from django.conf import settings
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from paypal.standard.ipn.models import PayPalIPN


IPN_POST_PARAMS = {
    "protection_eligibility":"Ineligible",
    "last_name":"User",
    "txn_id":"51403485VH153354B",
    "receiver_email":settings.PAYPAL_RECEIVER_EMAIL,
    "payment_status":"Completed",
    "payment_gross":"10.00",
    "tax":"0.00",
    "residence_country":"US",
    "invoice":"0004",
    "payer_status":"verified",
    "txn_type":"express_checkout",
    "handling_amount":"0.00",
    "payment_date":"23:04:06 Feb 02, 2009 PST",
    "first_name":"Test",
    "item_name":"",
    "charset":"windows-1252",
    "custom":"website_id=13&user_id=21",
    "notify_version":"2.6",
    "transaction_subject":"",
    "test_ipn":"1",
    "item_number":"",
    "receiver_id":"258DLEHY2BDK6",
    "payer_id":"BN5JZ2V7MLEV4",
    "verify_sign":"An5ns1Kso7MWUdW4ErQKJJJ4qi4-AqdZy6dD.sGO3sDhTf1wAbuO2IZ7",
    "payment_fee":"0.59",
    "mc_fee":"0.59",
    "mc_currency":"USD",
    "shipping":"0.00",
    "payer_email":"bishan_1233269544_per@gmail.com",
    "payment_type":"instant",
    "mc_gross":"10.00",
    "quantity":"1",
}


class DummyPayPalIPN(PayPalIPN):    
    def __init__(self, st='VERIFIED'):
        self.st = st
            
    def _postback(self, test=True):
        """Perform a Fake PayPal IPN Postback request."""
        return HttpResponse(self.st)


# @@@ Currently the flag_info doesn't seem to be set correctly.
class IPNTest(TestCase):    
    urls = 'paypal.standard.ipn.tests.test_urls'

    def test_correct_ipn(self):       
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        response = self.client.post("/ipn/", IPN_POST_PARAMS)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)        
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.flag, False)
  
    def test_incorrect_receiver_email(self):       
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        post_params = IPN_POST_PARAMS.copy()
        post_params.update({"receiver_email":"incorrect_email@someotherbusiness.com"})
        response = self.client.post("/ipn/", post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.flag, True)
        # self.assertEqual(ipn_obj.flag_info, "Invalid receiver_email.")
        
    def test_invalid_payment_status(self):       
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        post_params = IPN_POST_PARAMS.copy()
        post_params.update({"payment_status":"Failed",})            
        response = self.client.post("/ipn/", post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.flag, True)
        # self.assertEqual(ipn_obj.flag_info, "Invalid payment_status.")

    def test_duplicate_txn_id(self):       
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        post_params = IPN_POST_PARAMS.copy()
        response = self.client.post("/ipn/", post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.flag, False)
        post_params = IPN_POST_PARAMS  
        response = self.client.post("/ipn/", post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 2)
        ipn_obj = PayPalIPN.objects.all().order_by('-created_at')[0]
        self.assertEqual(ipn_obj.flag, True)
        # self.assertEqual(ipn_obj.flag_info, "Duplicate transaction ID.")
        
    def test_failed_ipn(self):
        self.dppipn = DummyPayPalIPN(st='INVALID')
        PayPalIPN._postback = self.dppipn._postback
        post_params = IPN_POST_PARAMS.copy()
        response = self.client.post("/ipn/", post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.flag, True)