#!/usr/bin/env python

from setuptools import setup, find_packages

import paypal

setup(
    name='django-paypal',
    version=".".join(map(str, paypal.__version__)),
    author='John Boxall',
    author_email='john@handimobility.ca',
    maintainer="David Cramer",
    maintainer_email="dcramer@gmail.com",
    url='http://github.com/johnboxall/django-paypal',
    install_requires=[
        'Django>=1.0'
    ],
    description = 'A pluggable Django application for integrating PayPal Payments Standard or Payments Pro',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
