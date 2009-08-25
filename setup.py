#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-paypal',
    version='TODO',
    author='John Boxall',
    author_email='john@handimobility.ca',
    url='http://github.com/johnboxall/django-paypal',
    install_requires=['django'],
    description = 'A pluggable Django application for integrating PayPal Payments Standard or Payments Pro',
    packages=find_packages(),
    include_package_data=True,
)
