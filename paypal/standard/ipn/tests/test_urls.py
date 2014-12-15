from django.conf.urls import patterns, url

from paypal.standard.ipn.views import IPNView

urlpatterns = patterns('paypal.standard.ipn.views',
    url(r'^ipn/$', IPNView.as_view()),
)
