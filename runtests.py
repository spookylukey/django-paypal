#!/usr/bin/env python
from __future__ import unicode_literals

import argparse
import sys
import warnings

from django.conf import settings
from django.core.management import execute_from_command_line

warnings.simplefilter("always", PendingDeprecationWarning)
warnings.simplefilter("always", DeprecationWarning)


parser = argparse.ArgumentParser(description="Run the test suite, or specific tests specified using dotted paths.")
parser.add_argument("--use-tz-false", action='store_true', default=False,
                    help="Set USE_TZ=False in settings")

known_args, remaining_args = parser.parse_known_args()

remaining_options = [a for a in remaining_args if a.startswith('-')]
test_args = [a for a in remaining_args if not a.startswith('-')]

settings_dict = dict(
    ROOT_URLCONF='',
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
    PAYPAL_TEST=True,
    # Please dont make me create another test account and remove this from here :)
    PAYPAL_WPP_USER='django.paypal.seller_api1.gmail.com',
    PAYPAL_WPP_PASSWORD='D5LBCTEKUUJR8EKL',
    PAYPAL_WPP_SIGNATURE='AFcWxV21C7fd0v3bYYYRCpSSRl31A6nHqN3IBok0TF-H8I-C8C6u41Do',
    PAYPAL_IDENTITY_TOKEN='xxx',
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.sessions',
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
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ],
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
            ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ],
    USE_TZ=not known_args.use_tz_false,
    LOGGING={
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'handlers': {
            'console': {
                'level': 'WARNING',
                'class': 'logging.StreamHandler',
            },
        },
    },
    )

settings.configure(**settings_dict)


if len(test_args) == 0:
    test_args = ["paypal.pro.tests", "paypal.standard.ipn.tests", "paypal.standard.pdt.tests"]

argv = [sys.argv[0], "test"] + remaining_options + test_args

if __name__ == '__main__':
    execute_from_command_line(argv)
