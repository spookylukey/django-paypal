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

* Django 1.6 to 1.8 on Python 2.7, 3.3 and 3.4.
* Django 1.9 on Python 2.7, 3.4 and 3.5.

Please read the docs if you are upgrading from Django 1.7

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

Please bear this in mind if filing an issue. If you discover a bug, unless it is
a critical data loss or security bug, the maintainers are unlikely to work for
free to fix it, and a new feature will only be added by the maintainers if they
need it themselves.

Contributing to django-paypal
=============================

If you want to contribute (yay!), please create a fork and start a branch off
'master' for your changes. Submit a PR on GitHub to request that it is merged.

In creating a pull request, it will help to remember that this project is in
maintenance mode. This means the maintainers merge patches, but not ones that
make more work for them in future, or do not benefit the other users of the
project - for example, code that is not covered by automated tests, or large
backwards incompatible changes that aren't necessary.

Remember that a new feature that is neither documented nor covered by tests is
not actually a contribution to the project, but only benefits the person who
“contributed” it, and so won't be accepted.

That said, if you do have large changes that you want to contribute, including
large new features (such as implementing newer PayPal payment methods), they
will be gladly accepted if they are implemented well.

In more detail, please see the following guidelines and hints:

**isort** keeps imports in order. Run **tox -e isort-check** to check your
imports, and **isort <PATHPATH>** to fix them. Use **# isort:skip** to
get imports to be ignored by isort.

All bug fixes and new features will require tests to accompany them, unless it
is very difficult to write the test (e.g. non deterministic behaviour). The
tests should fail without the fix/feature.

Please add to docs/release_notes.rst for any significant bug fixes or new features.

New features need documentation adding in docs/

See docs/tests.rst for info about running the test suite.

If you make changes to the models, please create migrations for both Django 1.7+
and South e.g.::

    ./manage.py makemigrations ipn

    ./manage.py schemamigration --auto ipn

If a pull request doesn't meet these requirements, and is not updated for 6
months after feedback is given to the author, it will be assumed they have lost
interest and the PR will be closed.

Contributors of any kind are expected to act with politeness to all other
contributors, in pull requests, issue trackers etc., and harassing behaviour
will not be tolerated.
