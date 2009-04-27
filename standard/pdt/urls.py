from django.conf.urls.defaults import *

urlpatterns = patterns('paypal.standard.pdt.views',
    url(r'^pdt/$', 'pdt', name="paypal-pdt"),
)