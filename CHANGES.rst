Change log
==========

Please always check the `database upgrading docs
<http://django-paypal.readthedocs.org/en/stable/updatedb.html>`_ when upgrading,
and see the `release_notes.rst
<https://django-paypal.readthedocs.org/en/stable/release_notes.html>`_ for
detailed information about all changes.

Below is a summary:

Version 0.2.3
-------------
* Fixed various deprecation warnings when running under Django 1.8


Version 0.2.2
-------------

* Added 'commit' kwarg to ``express_endpoint_for_token()``

Version 0.2.1
-------------

* Added ``PayPalNVP.response_dict`` attribute.
* Added ``PayPalFailure.nvp`` attribute to get full info
* Switched to using ``requests`` library for HTTP calls.

Version 0.2
-----------

* Introduced new, less confusing signals, and deprecated the old ones.  This is
  a bit of an API overhaul, but the migration path is clear, don't worry!

Version 0.1.5
-------------

* Fixed support for custom User model in South migrations

  If you:

  * are using a custom AUTH_USER_MODEL
  * are using the 'pro' app
  * installed version 0.1.4 and ran the migrations,

  you will need to reverse the migrations in the 'pro' app that were applied
  when you ran "./manage.py migrate".


Version 0.1.4
-------------

* New docs!

* Python 3 support.

* Django 1.7 support.

* Support for custom User model via AUTH_USER_MODEL. If you change AUTH_USER_MODEL
  you will still need to write your own migrations.

* Support for all possible 'initial' options that could be wanted in PayPalStandardForm

* Support for PayPalPro CreateBillingAgreement method

* Support for PayPalPro DoReferenceTransaction method

* Upgraded to PayPal Pro API version 116.0

  * This deprecates the "amt" parameter for SetExpressCheckout and
    DoExpressCheckoutPayment. paymentrequest_0_amt should be used instead. Use
    of amt will raise a DeprecationWarning for now.

* Various bug fixes, refactorings and small features.

* Removed PDT signals (which were never fired)

Version 0.1.3
-------------

* Missing payment types added

* Additional signals:

  * payment_was_refunded
  * payment_was_reversed

* Django 1.6 compatibility

* Various bug fixes, including:

  * Fixes for non-ASCII characters
