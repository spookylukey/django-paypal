Change log
==========

Version 0.2
-----------

* Introduced new, less confusing signals, and deprecated the old ones.  This is
  a bit of an API overhaul, but the migration path is clear, don't worry!

  * IPN:

    Previously, there were IPN signals like ``payment_was_successful`` which
    fired even if the ``payment_status`` on the IPN was ``'Failed'``, and there
    were other signals like ``payment_was_refunded`` to cover other specific
    statuses, but not all of them. There were also bugs that meant that some
    signals would never fire.

    To sort out all these issues, and to future proof the design, the signals
    have been reduced to:

    * ``valid_ipn_received``

    * ``invalid_ipn_received``

    The 'invalid' signals are sent when the transaction was flagged - because of
    a failed check with PayPal, for example, or a duplicate transaction ID.  You
    should never act on these, but might want to be notified of a problem.

    The 'valid' signals need to be handled. However, you will need to check the
    payment_status and other attributes to know what to do.

    The old signals still exist and are used, but are deprecated. They will be
    removed in version 1.0.


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

Version 0.1.3
-------------

* Missing payment types added

* Additional signals:

  * payment_was_refunded
  * payment_was_reversed

* Django 1.6 compatibility

* Various bug fixes, including:

  * Fixes for non-ASCII characters
