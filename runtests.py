#!/usr/bin/env python
import sys
import getpass

from os.path import dirname, abspath

from django.conf import settings

if not settings.configured:
    settings.configure(
        ROOT_URLCONF='',
        DATABASE_ENGINE='sqlite3',
        PAYPAL_RECEIVER_EMAIL='test@example.com',
        PAYPAL_TEST=True,
        # Please dont make me create another test account and remove this from here :)
        PAYPAL_WPP_USER='dcrame_1278645792_biz_api1.gmail.com',
        PAYPAL_WPP_PASSWORD='1278645801',
        PAYPAL_WPP_SIGNATURE='A4k1.O6xTyld5TiKeVmCuOgqzLRuAKuTtSG.7BD3R9E8SBa-J0pbUeYp',
        INSTALLED_APPS=[
            'paypal.pro',
            'paypal.standard',
            'paypal.standard.ipn',
            # 'paypal.standard.pdt', # we need the PDT token
        ]
    )

from django.test.simple import run_tests


def runtests(*test_args):
    if not test_args:
        test_args = ['pro', 'standard', 'ipn']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])