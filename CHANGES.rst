Change log
==========

Please always check the `database upgrading docs
<http://django-paypal.readthedocs.org/en/stable/updatedb.html>`_ when upgrading,
and see the `release_notes.rst
<https://django-paypal.readthedocs.org/en/stable/release_notes.html>`_ for
notes that are too long to fit here.


Version 0.3.0 (in development)
------------------------------

* Dropped support for Django 1.4 and 1.5.
* Fixed crasher with AmbiguousTimeError.
* Better logging for paypal.pro.
* Fixed Django 1.7/1.8 compat for EmailField.
* Added missing migration for PDT model.
* Added missing South migrations
* Fixed max_length of IPN/PDT ``custom`` and ``transaction_subject`` fields
* Fixed issue #105 - IPN failure when running under non-English locale

* *IMPORTANT:* Deprecated the ``PAYPAL_RECEIVER_EMAIL`` setting to allow
  multiple receiver emails in a single app. This has several consequences for
  your code, which must be fixed before upgrading to 0.4.x, when this setting
  will be dropped entirely:

  * When creating a ``PayPalPaymentsForm`` you must provide the ``business``
    field in the ``initial`` parameter.

  * Validation of ``receiver_email`` must be done in your ``valid_ipn_received``
    signal handler and your PDT processing view. Take into account the fact that
    the user can tamper with the form fields before posting them to PayPal.

* The use of the ``pdt`` view for PDT payments is deprecated. Now you should
  provide your own view and use the ``process_pdt`` helper function.

Version 0.2.7
-------------

* Small fix to logging, thanks frankier

Version 0.2.6
-------------

* Small fixes, including not depending on South.

Version 0.2.5
-------------

* Fixed some ``PayPalIPN`` DateTimeFields that were not being handled like the rest. Thanks
  thiagogds for the patch.

* Fixed ``PayPalNVP.timestamp`` field so that it receives timezone-aware datetimes
  if you have ``USE_TZ = True``


Version 0.2.4
-------------

* Fixed timezone parsing of PalPal data so that ``PayPalIPN.payment_date`` and others
  are handled correctly (if you have ``USE_TZ = True``).

  This does not include a migration to fix old data - see the release notes if
  you need that.

* Work-arounds for bugs in the IPN Simulator
* Other small fixes


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
