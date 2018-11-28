#!/usr/bin/env python

# This manage.py exists for the purpose of creating migrations
import sys

from django.conf import settings
from django.core.management import execute_from_command_line

settings.configure(
    ROOT_URLCONF='paypal.standard.ipn.tests.test_urls',
    DATABASES={'default':
               {'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'test.db',
                }},
    PAYPAL_IDENTITY_TOKEN='',
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'paypal.pro',
        'paypal.standard',
        'paypal.standard.ipn',
        'paypal.standard.pdt',
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

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
