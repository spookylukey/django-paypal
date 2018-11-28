Release process
---------------

* Run all tests::

    tox

  Or check Travis, if it has run against the latest source code:
  https://travis-ci.org/spookylukey/django-paypal

* Change docs/release_notes.rst to remove " (under development)"

* Update version numbers:

  * ``paypal/__init__.py``
  * ``setup.py``
  * ``docs/conf.py``

* Ensure correct file permissions::

  $ chmod ugo+r -R *

* Commit

* Release to PyPI::

    $ umask 000
    $ ./setup.py sdist bdist_wheel
    $ twine upload dist/django_paypal-$VERSION-py2.py3-none-any.whl dist/django-paypal-$VERSION.tar.gz

* Tag and push, for example.::

    git tag v0.1.6
    git push
    git push --tags


Post release
------------

* Bump version numbers to next version with ``-dev1`` suffix, for example ``0.1.7-dev1``

* Add new section to docs/release_notes.rst, with " (under development)".

* Commit
