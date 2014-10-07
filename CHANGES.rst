Change log
==========

Version 0.1.4
-------------

* Python 3 support.

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
