Update the database
===================

django-paypal uses South for migrations for Django < 1.7, and the built in
Django migrations framework for Django >= 1.7.

To update your database:

* For Django < 1.7:

  * Ensure South is installed if it isn't already:

      * Do::

          pip install 'South>=1.0.1'

      * Add 'south' to your `INSTALLED_APPS` setting.

      * Run the following to install South tables::

          ./manage.py syncdb

  * Then for each time you install or upgrade django-paypal, run::

      ./manage.py migrate


* For Django >= 1.7, do::

  ./manage.py migrate


Upgrading from previous versions
--------------------------------

If you using Django < 1.7 and are upgrading from a version that wasn't using
South, you will have to use ``--fake`` - see
http://south.readthedocs.org/en/latest/commands.html?highlight=fake

It will probably look something like::

    ./manage.py migrate ipn --fake --initial
    ./manage.py migrate pdt --fake --initial
    ./manage.py migrate pro --fake --initial

depending on what apps you have installed.

Upgrading to Django 1.7
-----------------------

In Django 1.7, the migration framework is good at automatically noticing
migrations that have been applied and not applying them twice. So you should be
able to switch to Django 1.7 at any point.
