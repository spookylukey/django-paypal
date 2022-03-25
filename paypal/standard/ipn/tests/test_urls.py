try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

from django.contrib import admin

from paypal.standard.ipn import views

urlpatterns = [
    re_path(r"^ipn/$", views.ipn),
    re_path(r"^admin/", admin.site.urls),
]
