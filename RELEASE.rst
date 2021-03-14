Release process
---------------

* Run all tests::

    tox

* Change docs/release_notes.rst to remove "under development" and replace with
  date.

* Update version numbers:

  * ``paypal/__init__.py``
  * ``setup.py``
  * ``docs/conf.py``

* Commit

* Release to PyPI::

    $ ./release.sh

* Tag and push, for example.::

    git tag v0.1.6
    git push
    git push --tags


Post release
------------

* Bump version numbers to next version with ``.dev1`` suffix, for example ``0.1.7.dev1``

* Add new section to docs/release_notes.rst, with " (under development)".

* Commit
