try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

from paypal.standard.ipn import views

urlpatterns = [
    re_path(r"^$", views.ipn, name="paypal-ipn"),
]
