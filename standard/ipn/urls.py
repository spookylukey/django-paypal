from django.conf.urls.defaults import *



urlpatterns = patterns('paypal.standard.ipn.views',            
            url(r'^ipn/$', 'ipn', name="paypal-ipn"),
        )


urlpatterns += patterns('paypal.standard.ipn.tests',
        url(r'^fake_ipn_response/?$', 'ipn.fake_ipn_response', name="paypal-fake-ipn-response"),
        )