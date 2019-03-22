#!/bin/sh

umask 000
rm -rf build dist
git ls-tree --full-tree --name-only -r HEAD | xargs chmod ugo+r
find . -type d | xargs chmod ugo+rx

./setup.py sdist bdist_wheel || exit 1

VERSION=$(./setup.py --version) || exit 1

twine upload dist/django-paypal-$VERSION.tar.gz dist/django_paypal-$VERSION-py2.py3-none-any.whl || exit 1
