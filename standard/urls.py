from django.conf.urls.defaults import *



urlpatterns = patterns('paypal.standard.views',
            url(r'^pdt/$', 'pdt', name="paypal-pdt"),
            url(r'^ipn/$', 'ipn', name="paypal-ipn"),
        )


urlpatterns += patterns('paypal.standard.tests',
        url(r'^fake_pdt_response/?$', 'pdt.fake_pdt_response', name="paypal-fake-pdt-response"),
        url(r'^fake_ipn_response/?$', 'ipn.fake_ipn_response', name="paypal-fake-ipn-response"),
        )