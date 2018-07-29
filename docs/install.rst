Install
=======

Install into a virtualenv using pip::

    pip install django-paypal


Or using the latest version from GitHub::

    pip install git://github.com/spookylukey/django-paypal.git#egg=django-paypal

If you are using Django < 1.11, you should use django-paypal 0.5.x and refer to
its documentation.

You will also need to edit your ``settings.py``, but the specifics depend on
whether you are using IPN/PDT/Pro.

In addition, you may need to take some precautions regarding ``REMOTE_ADDR``. In
all cases the user's IP address is recorded when payments are recorded, since
this value can be useful in some cases. This value is taken from
``request.META['REMOTE_ADDR']``. In some setups, however, it is possible that
this value is incorrect, or may not even validate as an IP address. If it is not
a valid IP address, then saving of IPN/PDT/NVP data will fail with a validation
error.

Due to the many different ways that systems can be configured, with different
proxies etc., correcting ``REMOTE_ADDR`` is outside the scope of django-paypal.
You are advised to use a custom middleware or a solution like `django-xff
<https://pypi.python.org/pypi/django-xff/>`_ to ensure that
``request.META['REMOTE_ADDR']`` is correct or at least a valid IP address.
