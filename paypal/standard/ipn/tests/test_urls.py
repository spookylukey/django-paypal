from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin

from paypal.standard.ipn import views

urlpatterns = [
    url(r'^ipn/$', views.ipn),
    url(r'^admin/', admin.site.urls),
]
