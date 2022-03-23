Django PayPal
=============


.. image:: https://github.com/spookylukey/django-paypal/workflows/build/badge.svg
   :target: https://github.com/spookylukey/django-paypal/actions?query=workflow%3Abuild+branch%3Amaster

.. image:: https://badge.fury.io/py/django-paypal.svg
    :target: https://badge.fury.io/py/django-paypal
    :alt: Latest PyPI version

Django PayPal is a pluggable application that integrates with PayPal Payments
Standard and Payments Pro.

See https://django-paypal.readthedocs.org/ for documentation.

django-paypal supports:

* Django 2.2 and later
* Python 3.6 and later


Project status
==============

This is an Open Source project that is *active* but in *maintenance mode*. The
maintainers see their primary responsibilities as:

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
using the issue tracker and pull requests. Please do not open issues for support
requests.

Questions and issues
====================

If you have a question about using django-paypal, see the
`Discussion <https://github.com/spookylukey/django-paypal/discussions>`_ section.
Only use the `issues <https://github.com/spookylukey/django-paypal/issues>`_ if
you are reporting a bug, or describing a new feature that you would like
to contribute.

Paid support
============

Some of the maintainers may be able to provide support on a paid basis for this
Open Source project. This includes the following kinds of things:

* Paying for bug fixes or new features (with the understanding that these
  changes will become freely available as part of the project and are not
  'owned' by the person who paid for them).

* Debugging or other support for integrating django-paypal into your project.

* Implementing the integration for you from scratch.

If you are interested in these, you can contact the following developers:

* Luke Plant - `homepage <https://lukeplant.me.uk>`_,
  `email <L.Plant.98@cantab.net>`_ - long time Django expert and contributor
  - see his `status page <https://lukeplant.me.uk/development-work.html>`_ before contacting.
