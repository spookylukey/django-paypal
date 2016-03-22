Release process
---------------

* Change docs/release_notes.rst to remove " (under development)"

* Run all tests::

    tox

* Update version numbers:

  * ``paypal/__init__.py``
  * ``setup.py``
  * ``docs/conf.py``

* Commit

* Release to PyPI::

    ./setup.py sdist bdist_wheel register upload

* Tag and push, for example.::

    git tag v0.1.6
    git push
    git push --tags


Post release
------------

* Bump version numbers to next version with ``-dev`` suffix, for example ``0.1.7-dev``

* Add new section to docs/release_notes.rst, with " (under development)".

* Commit
