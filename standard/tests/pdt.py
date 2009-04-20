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

def fake_pdt_response(request):
    st = request.GET.get('st', 'SUCCESS')
    custom = request.GET.get('custom', 'cb736658-3aad-4694-956f-d0aeade80194')
    txn_id = request.GET.get('txn_id', '1ED550410S3402306')
    mc_gross = request.GET.get('mc_gross', '225.00')
    c = RequestContext(request, locals())
    return render_to_response('standard/fake_pdt_response.html', c)

class PDTTest(TestCase):    
    def setUp(self):
        
        #import ipdb; ipdb.set_trace()
        paypal.standard.models.POSTBACK_ENDPOINT = reverse('paypal-fake-pdt-response')
        paypal.standard.models.SANDBOX_POSTBACK_ENDPOINT = reverse('paypal-fake-pdt-response')
        settings.PAYPAL_TESTING=True
        
        
        self.signals_flag = False
        
        # Every test needs a client.
        self.client = Client()

    def test_parse_paypal_response(self):
        paypal_response = self.client.get(reverse('paypal-fake-pdt-response'))
        self.assertContains(paypal_response, 'SUCCESS', status_code=200)
        
        self.assertEqual(paypal.standard.models.POSTBACK_ENDPOINT, reverse('paypal-fake-pdt-response'))
        self.assertEqual(paypal.standard.models.SANDBOX_POSTBACK_ENDPOINT, reverse('paypal-fake-pdt-response'))
                         
        
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        
        pdt_obj = PayPalPDT()
        pdt_obj.ipaddress = '127.0.0.1'
        
        pdt_obj._parse_paypal_response(paypal_response.content)
        
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalPDT.objects.all()), 1)
        
        pdt_obj = PayPalPDT.objects.all()[0]
        self.assertEqual(pdt_obj.txn_id, '1ED550410S3402306')
        
        
    def test_pdt(self):
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        get_params = {"tx":"4WJ86550014687441&st=Completed", "amt":"225.00", "cc":"EUR",
                      "cm":"a3e192b8%2d8fea%2d4a86%2db2e8%2dd5bf502e36be", "item_number":"",
                      "sig":"blahblahblah"}
        
        paypal_response = self.client.get(reverse('paypal-pdt'), get_params)
        self.assertContains(paypal_response, 'Transaction complete', status_code=200)
        
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalPDT.objects.all()), 1)

    def test_pdt_signals(self):
        self.assertEqual(self.signals_flag, False)        
        
        def successful_pdt(sender, **kwargs):
            log.info("successful pdt")
            self.signals_flag = True            
        
        pdt_successful.connect(successful_pdt)
        
        
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        get_params = {"tx":"4WJ86550014687441", "st":"Completed", "amt":"225.00", "cc":"EUR",
                      "cm":"a3e192b8%2d8fea%2d4a86%2db2e8%2dd5bf502e36be", "item_number":"",
                      "sig":"blahblahblah"}
        paypal_response = self.client.get(reverse('paypal-pdt'), get_params)
        self.assertContains(paypal_response, 'Transaction complete', status_code=200)
        
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalPDT.objects.all()), 1)
        self.assertEqual(self.signals_flag, True)

        # we don't want a new pdt for the same parameters
        paypal_response = self.client.get(reverse('paypal-pdt'), get_params)
        self.assertContains(paypal_response, 'Transaction complete', status_code=200)
        
        self.assertEqual(len(PayPalIPN.objects.all()), 0)
        self.assertEqual(len(PayPalPDT.objects.all()), 1)
        




    
    