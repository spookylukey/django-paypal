#!/usr/bin/env python

from setuptools import setup, find_packages

import paypal

setup(
    name='django-paypal',
    version=".".join(map(str, paypal.__version__)),
    author='John Boxall',
    author_email='john@handimobility.ca',
    maintainer="Luke Plant",
    maintainer_email="L.Plant.98@cantab.net",
    url='http://github.com/dcramer/django-paypal',
    install_requires=[
        'Django>=1.4'
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
