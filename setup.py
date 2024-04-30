#!/usr/bin/env python

import os.path

from setuptools import find_packages, setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


DESCRIPTION = "A pluggable Django application for integrating PayPal Payments Standard or Payments Pro"
URL = "https://github.com/spookylukey/django-paypal"
DOCS_URL = "https://django-paypal.readthedocs.org"

setup(
    name="django-paypal",
    version="2.1",
    author="John Boxall",
    author_email="john@handimobility.ca",
    maintainer="Luke Plant",
    maintainer_email="L.Plant.98@cantab.net",
    url=URL,
    python_requires=">=3.6",
    install_requires=[
        "Django>=2.2",
        "requests>=2.5.3",
        "pytz>=2015.4",
    ],
    description=DESCRIPTION,
    long_description=f"{DESCRIPTION}\n\nHome page: {URL}\n\nDocs: {DOCS_URL}\n",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 4.0",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
