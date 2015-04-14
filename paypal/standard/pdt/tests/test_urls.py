from django.conf.urls import url

from paypal.standard.pdt import views

urlpatterns = [
    url(r'^pdt/$', views.pdt),
]
