#!/usr/bin/env python
import sys

import django
from django.conf import settings

import warnings
warnings.simplefilter("always", PendingDeprecationWarning)
warnings.simplefilter("always", DeprecationWarning)

settings.configure(
    ROOT_URLCONF='',
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
    PAYPAL_RECEIVER_EMAIL='test@example.com',
    PAYPAL_TEST=True,
    # Please dont make me create another test account and remove this from here :)
    PAYPAL_WPP_USER='dcrame_1278645792_biz_api1.gmail.com',
    PAYPAL_WPP_PASSWORD='1278645801',
    PAYPAL_WPP_SIGNATURE='A4k1.O6xTyld5TiKeVmCuOgqzLRuAKuTtSG.7BD3R9E8SBa-J0pbUeYp',
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'paypal.pro',
        'paypal.standard',
        'paypal.standard.ipn',
        # 'paypal.standard.pdt', # we need the PDT token
    ],
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            'TIMEOUT': 0,
            'KEY_PREFIX': 'paypal_tests_',
        }
    },
    MIDDLEWARE_CLASSES=[],
)


from django.core.management import execute_from_command_line
argv = [sys.argv[0], "test"]

if len(sys.argv) == 1:
    # Nothing following 'runtests.py':
    if django.VERSION < (1,6):
        argv.extend(["pro", "ipn"])
    else:
        argv.extend(["paypal.pro.tests", "paypal.standard.ipn.tests"])
else:
    # Allow tests to be specified:
    argv.extend(sys.argv[1:])

if __name__ == '__main__':
    execute_from_command_line(argv)
