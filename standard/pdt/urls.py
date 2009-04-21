from django.conf.urls.defaults import *



urlpatterns = patterns('paypal.standard.pdt.views',
            url(r'^pdt/$', 'pdt', name="paypal-pdt"),
        )


urlpatterns += patterns('paypal.standard.pdt.tests',
        url(r'^fake_pdt_response/?$', 'pdt.fake_pdt_response', name="paypal-fake-pdt-response"),        
        )