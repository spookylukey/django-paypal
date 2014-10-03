#!/usr/bin/env python

# This manage.py exists for the purpose of creating migrations
import sys

from django.conf import settings

settings.configure(
    ROOT_URLCONF='',
    DATABASES={'default':
               {'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'test.db',
                }},
    PAYPAL_RECEIVER_EMAIL='',
    PAYPAL_IDENTITY_TOKEN='',
    INSTALLED_APPS=[
        'django.contrib.auth',
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

from django.core.management import execute_from_command_line
if __name__ == '__main__':
    execute_from_command_line(sys.argv)
