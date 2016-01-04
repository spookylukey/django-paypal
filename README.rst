Django PayPal
=============

.. image:: https://travis-ci.org/spookylukey/django-paypal.svg?branch=master
    :target: https://travis-ci.org/spookylukey/django-paypal
    :alt: Build Status

.. image:: https://pypip.in/v/django-paypal/badge.png
    :target: https://pypi.python.org/pypi/django-paypal
    :alt: Latest PyPI version

Django PayPal is a pluggable application that integrates with PayPal Payments
Standard and Payments Pro.

See https://django-paypal.readthedocs.org/ for documentation.

django-paypal supports:

* Django 1.6 to 1.8 on Python 2.7, 3.3 and 3.4. from version 1.6 to 1.9.
* Django 1.9 on Python 2.7, 3.4 and 3.5.

Please read the docs if you are upgrading from Django 1.7


Contributing to django-paypal
=============================

If you want to contribute (yay!), please create a fork and start a branch off
'master' for your changes. Submit a PR on GitHub to request that it is merged.

All bug fixes and new features will require tests to accompany them, unless it
is very difficult to write the test (e.g. non deterministic behaviour). The
tests should fail without the fix/feature.

Please add to CHANGES.rst for any significant bug fixes or new features. This
file becomes part of the PyPI description for the package.

New features need documentation adding in docs/

See docs/tests.rst for info about running the test suite.

If you make changes to the models, please create migrations for both Django 1.7+
and South e.g.::

    ./manage.py makemigrations ipn

    ./manage.py schemamigration --auto ipn
