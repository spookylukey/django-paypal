Django PayPal
=============

.. image:: https://travis-ci.org/spookylukey/django-paypal.svg?branch=master
    :target: https://travis-ci.org/spookylukey/django-paypal
    :alt: Build Status

.. image:: https://badge.fury.io/py/django-paypal.svg
    :target: https://badge.fury.io/py/django-paypal
    :alt: Latest PyPI version

Django PayPal is a pluggable application that integrates with PayPal Payments
Standard and Payments Pro.

See https://django-paypal.readthedocs.org/ for documentation.

django-paypal supports:

* Django 1.11+
* Python 2.7, and 3.4+

(Not all combinations are supported).

Project status
==============

This project is *active* but in *maintenance mode*. The maintainers see their
primary responsibilities as:

* fixing any critical data loss or security bugs.
* keeping the project up-to-date with new versions of Django (or other
  dependencies).
* merging well written patches from the community, and doing so promptly.

Large scale development work and feature additions are not planned by the
maintainers.

Some important parts of the code base are not covered by automated tests, and
may be broken for some versions of Django or Python. These parts of the code
base currently issue warnings, and the maintainers are waiting for tests to be
contributed by those who actually need those parts, and docs where appropriate.

Please bear these things in mind if filing an issue. If you discover a bug,
unless it is a critical data loss or security bug, the maintainers are unlikely
to work for free to fix it, and a new feature, or tests for existing
functionality, will only be added by the maintainers if they need it themselves.

That said, if you do have large changes that you want to contribute, including
large new features (such as implementing newer PayPal payment methods), they
will be gladly accepted if they are implemented well.

Please see `CONTRIBUTING.rst <CONTRIBUTING.rst>`_ for more information about
using the issue tracker and pull requests.
