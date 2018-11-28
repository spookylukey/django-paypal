Update the database
===================

django-paypal uses the built in Django migrations framework.

To update your database:

    ./manage.py migrate

If you using or upgrading from much older versions of Django (e.g. before 1.7
which didn't have a built in migrations framework), please upgrade to
django-paypal 0.5.x first and follow the docs found in that version.
