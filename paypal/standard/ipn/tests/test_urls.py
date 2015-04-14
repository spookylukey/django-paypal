from django.conf.urls import url

from paypal.standard.ipn import views

urlpatterns = [
    url(r'^ipn/$', views.ipn),
]
