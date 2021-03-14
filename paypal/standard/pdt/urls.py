from __future__ import unicode_literals

try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

from paypal.standard.pdt import views

urlpatterns = [
    re_path(r'^$', views.pdt, name="paypal-pdt"),
]
