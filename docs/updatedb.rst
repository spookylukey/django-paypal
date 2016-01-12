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


* For Django >= 1.7::

    ./manage.py migrate


Upgrading from very old versions
--------------------------------

If you using Django < 1.7 and are upgrading from a very old version (before
0.1.1) that wasn't using South, you will have to use ``--fake`` - see
http://south.readthedocs.org/en/latest/commands.html?highlight=fake

It will probably look something like::

    ./manage.py migrate ipn --fake --initial
    ./manage.py migrate pdt --fake --initial
    ./manage.py migrate pro --fake --initial
    ./manage.py migrate ipn
    ./manage.py migrate pdt
    ./manage.py migrate pro

depending on what apps you have installed.

Please also see :doc:`release_notes`.

Upgrading to Django 1.7
-----------------------

If you installed django-paypal with an older version of Django, you will have
been using South to handle database migrations. Due to the new built-in database
migration framework in Django 1.7, the upgrade procedure is slightly
complicated.

The recommended upgrade procedure is:

* Before upgrading to Django 1.7, first upgrade django-paypal to the latest
  version and run migrations as above (including deploying to your production
  environment and running migrations there).

* Then upgrade Django to 1.7, and run the following as appropriate for your
  situation::

    ./manage.py migrate ipn --fake
    ./manage.py migrate pdt --fake
    ./manage.py migrate pro --fake

  In this way, you can avoid running equivalent migrations twice (the South versions
  and the Django built-in versions).
