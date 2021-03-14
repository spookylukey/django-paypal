Issue tracker and support requests
==================================

The GitHub issue tracker is for reporting bugs in django-paypal, or proposed
features. It is not for support requests - please see the `django-paypal docs
<https://django-paypal.readthedocs.org/>`_ , or the relevant PayPal docs. Issues
(or emails to the maintainers) that are really support requests and do not
involve fixing django-paypal (or its docs) will be ignored/closed. If you do not
know why your code does not work, we're afraid we cannot provide any help, and
your issue will be closed immediately if you open one.

If, however, you have found the cause of the problem and it is a bug with
django-paypal (including anything lacking in the documentation), or another
suggestion for how django-paypal can be improved, please do open a ticket.


Contributing changes to django-paypal
=====================================

If you want to contribute (yay!), please create a fork and start a branch off
'master' for your changes. Submit a PR on GitHub to request that it is merged.

Since this project is in maintenance mode, the maintainers will merge patches,
but not ones that make more work for them in future, or do not benefit the other
users of the project - for example, code that is not covered by automated tests,
or large backwards incompatible changes that aren't necessary.

Remember that a new feature that is neither documented nor covered by tests is
not actually a contribution to the project, but only benefits the person who
“contributed” it, and so won't be accepted.

Patches that are not of sufficient quality will be labelled
``patch-needs-improvement`` in GitHub with comments added explaining why, and in
general the original author, not the maintainers, will be expected to do this
improvement.

In more detail, please see the following guidelines and hints:

Development environment
~~~~~~~~~~~~~~~~~~~~~~~

1. Clone your GitHub repo

2. Create a virtualenv, using one of the supported versions of Python.

3. Run ``python setup.py develop``

4. Install development tools::

     pip install tox isort flake8

5. Recommended: Install `pre-commit <https://pre-commit.com/>`_ and set up
   the hooks::

       pre-commit install

   This will run flake8/isort automatically when you commit.

Code quality
~~~~~~~~~~~~

**isort** keeps imports in order. Run **tox -e isort-check** to check your
imports, and **isort <PATHPATH>** to fix them. Use **# isort:skip** to
get imports to be ignored by isort.

All bug fixes and new features will require tests to accompany them, unless it
is very difficult to write the test (e.g. non deterministic behaviour). The
tests should fail without the fix/feature.

Please add to ``docs/release_notes.rst`` for any significant bug fixes or new features.

New features need documentation adding in ``docs/``

See ``docs/tests.rst`` for info about running the test suite.

If you make changes to the models, please create migrations e.g.::

    ./manage.py makemigrations ipn

If a pull request doesn't meet these requirements, and is not updated for 6
months after feedback is given to the author, it will be assumed they have lost
interest and the PR will be closed.

Conduct
=======

Contributors of any kind are expected to act with politeness to all other
contributors, in pull requests, issue trackers etc., and harassing behaviour
will not be tolerated.
