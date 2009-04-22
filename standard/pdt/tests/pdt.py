"""
run this with ./manage.py test website
see http://www.djangoproject.com/documentation/testing/ for details
"""
from django.test import TestCase
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpRequest, QueryDict
from paypal.standard.pdt.models import PayPalPDT
from paypal.standard.pdt.forms import PayPalPDTForm
from paypal.standard.pdt.signals import pdt_successful, pdt_failed
from paypal.standard.pdt.views import pdt as pdt_view
from django.conf import settings

def fake_pdt_response(fake_request={}):
    st = fake_request.get('st', 'SUCCESS')
    custom = fake_request.get('custom', 'cb736658-3aad-4694-956f-d0aeade80194')
    txn_id = fake_request.get('txn_id', '1ED550410S3402306')
    mc_gross = fake_request.get('mc_gross', '225.00')
    business_email = fake_request.get('business', settings.PAYPAL_RECEIVER_EMAIL)
    c = RequestContext(fake_request, locals())
    return render_to_response('pdt/fake_pdt_response.html', c)

class DummyPayPalPDT(PayPalPDT):
    class Meta:
        proxy = True
            
    def _postback(self, test=True):
        """
        Perform PayPal PDT Postback validation.
        Sends the transaction id and busines paypal token data back to PayPal which responds with SUCCESS or FAILED.
        Returns True if the postback is successful.
        
        """
        fake_request = {'custom': self.cm, 'txn_id': self.tx, 'mc_gross': self.amt}
        response = fake_pdt_response(fake_request)
        return self._parse_paypal_response(response.content)

class DummyPayPalPDTForm(PayPalPDTForm):    
    class Meta:
        model=DummyPayPalPDT

class PDTTest(TestCase):    
    def setUp(self):
        self.signals_flag = False        

    def test_parse_paypal_response(self):
        paypal_response = fake_pdt_response()
        self.assertContains(paypal_response, 'SUCCESS', status_code=200)        
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        pdt_obj = DummyPayPalPDT()
        pdt_obj.ipaddress = '127.0.0.1'
        pdt_obj._parse_paypal_response(paypal_response.content)
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        self.assertEqual(pdt_obj.txn_id, '1ED550410S3402306')
        
        
    def test_pdt(self):        
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        get_params = {"tx":"4WJ86550014687441", "st":"Completed", "amt":"225.00", "cc":"EUR",
                      "cm":"a3e192b8%2d8fea%2d4a86%2db2e8%2dd5bf502e36be", "item_number":"",
                      "sig":"blahblahblah"}
        qd = QueryDict('', mutable=True)
        qd.update(get_params)    
        request = HttpRequest()
        request.GET = qd
        request.method = 'GET'
        paypal_response = pdt_view(request, model_class=DummyPayPalPDT, form_class=DummyPayPalPDTForm)
        self.assertContains(paypal_response, 'Transaction complete', status_code=200)
        self.assertEqual(len(PayPalPDT.objects.all()), 1)

    def test_pdt_signals(self):
        self.assertEqual(self.signals_flag, False)        
        
        def successful_pdt(sender, **kwargs):
            self.signals_flag = True            
        
        pdt_successful.connect(successful_pdt)
        
        self.assertEqual(len(PayPalPDT.objects.all()), 0)
        get_params = {"tx":"4WJ86550014687441", "st":"Completed", "amt":"225.00", "cc":"EUR",
                      "cm":"a3e192b8%2d8fea%2d4a86%2db2e8%2dd5bf502e36be", "item_number":"",
                      "sig":"blahblahblah"}
        qd = QueryDict('', mutable=True)
        qd.update(get_params)    
        request = HttpRequest()
        request.GET = qd
        request.method = 'GET'
        paypal_response = pdt_view(request, model_class=DummyPayPalPDT, form_class=DummyPayPalPDTForm)
        self.assertContains(paypal_response, 'Transaction complete', status_code=200)
        
        self.assertEqual(len(PayPalPDT.objects.all()), 1)
        self.assertEqual(self.signals_flag, True)
        
        pdt_obj = PayPalPDT.objects.all()[0]
        self.assertEqual(pdt_obj.flag, False)
        
    def test_double_pdt_get(self):
        self.assertEqual(len(PayPalPDT.objects.all()), 0)        
        
        
        get_params = {"tx":"4WJ86550014687441", "st":"Completed", "amt":"225.00", "cc":"EUR",
                      "cm":"a3e192b8%2d8fea%2d4a86%2db2e8%2dd5bf502e36be", "item_number":"",
                      "sig":"blahblahblah"}
        qd = QueryDict('', mutable=True)
        qd.update(get_params)    
        request = HttpRequest()
        request.GET = qd
        request.method = 'GET'
        paypal_response = pdt_view(request, model_class=DummyPayPalPDT, form_class=DummyPayPalPDTForm)
        self.assertContains(paypal_response, 'Transaction complete', status_code=200)
        self.assertEqual(len(PayPalPDT.objects.all()), 1)
        
        pdt_obj = PayPalPDT.objects.all()[0]
        self.assertEqual(pdt_obj.flag, False)
        
        paypal_response = pdt_view(request, model_class=DummyPayPalPDT, form_class=DummyPayPalPDTForm)
        self.assertContains(paypal_response, 'Transaction complete', status_code=200)
        self.assertEqual(len(PayPalPDT.objects.all()), 1) # we don't create a new pdt
        
        pdt_obj = PayPalPDT.objects.all()[0]
        self.assertEqual(pdt_obj.flag, False)




    
    