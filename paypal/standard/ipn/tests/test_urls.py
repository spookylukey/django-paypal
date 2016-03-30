from __future__ import unicode_literals

from django.conf.urls import url

from paypal.standard.ipn import views
from django.contrib import admin

urlpatterns = [
    url(r'^ipn/$', views.ipn),
    url(r'^admin/', admin.site.urls),
]
