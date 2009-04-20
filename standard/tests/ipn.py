"""
run this with ./manage.py test website
see http://www.djangoproject.com/documentation/testing/ for details
"""
from django.test import TestCase
from django.test.client import Client
from django.shortcuts import render_to_response
from django.template import RequestContext
from paypal.standard.models import PayPalIPN, PayPalPDT
from paypal.standard.signals import pdt_successful, pdt_failed
import logging
from django.conf import settings
import paypal
from django.core.urlresolvers import reverse


log = logging.getLogger("pdt tests")


IPN_POST_PARAMS = {"protection_eligibility":"Ineligible",
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
    "quantity":"1",}

def fake_ipn_response(request):
    st = request.GET.get('st', 'VERIFIED')    
    c = RequestContext(request, locals())
    return render_to_response('standard/fake_ipn_response.html', c)



class IPNTest(TestCase):    
    def setUp(self):
        
        #import ipdb; ipdb.set_trace()
        paypal.standard.models.POSTBACK_ENDPOINT = reverse('paypal-fake-ipn-response')
        paypal.standard.models.SANDBOX_POSTBACK_ENDPOINT = reverse('paypal-fake-ipn-response')
        settings.PAYPAL_TESTING=True
        
        
        self.signals_flag = False
        
        # Every test needs a client.
        self.client = Client()        
        
    def test_correct_ipn(self):       
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)        
        post_params = IPN_POST_PARAMS.copy()        
        response = self.client.post(reverse('paypal-ipn'), post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.flag, False)

  
    def test_incorrect_receiver_email(self):
       
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        
        post_params = IPN_POST_PARAMS.copy()
        post_params.update({"receiver_email":"incorrect_email@someotherbusiness.com"})
        response = self.client.post(reverse('paypal-ipn'), post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.flag, True)
        self.assertEqual(ipn_obj.flag_info, "Invalid receiver_email.")
        
    def test_invalid_payment_status(self):       
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        
        post_params = IPN_POST_PARAMS.copy()
        post_params.update({"payment_status":"Failed",})            
        response = self.client.post(reverse('paypal-ipn'), post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.flag, True)
        self.assertEqual(ipn_obj.flag_info, "Invalid payment_status.")

    def test_duplicate_txn_id(self):       
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)        
        post_params = IPN_POST_PARAMS.copy()        
        response = self.client.post(reverse('paypal-ipn'), post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 1)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        
        ipn_obj = PayPalIPN.objects.all()[0]
        self.assertEqual(ipn_obj.flag, False)
        
        post_params = IPN_POST_PARAMS.copy()  
        response = self.client.post(reverse('paypal-ipn'), post_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PayPalIPN.objects.all()), 2)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        
        ipn_obj = PayPalIPN.objects.all().order_by('-created_at')[0]
        self.assertEqual(ipn_obj.flag, True)
        self.assertEqual(ipn_obj.flag_info, "Duplicate transaction ID.")