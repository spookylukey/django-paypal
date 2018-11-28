===============
 Release notes
===============


Version 1.0 (under development)
-------------------------------

* Dropped support for versions of Django before 1.11

* Encrypted button corrections

* .encode() the encrypted result to avoid b'' decoration under Python 3

* Fix the encrypted button examples in the documentation to use the encrypted form

* Fixed issue #206 - DB migration required by Django 2.1

* Support for almost all deprecated features removed, including:

  * Signals deprecated in v0.2 (see notes below)
  * Not passing ``nvp_handler`` to ``PayPalPro`` (see notes under 0.2)
  * Using ``"amt"`` parameter with ``SetExpressCheckout`` and
    ``DoExpressCheckoutPayment`` (see notes under 0.1.4 below)
  * Settings deprecated in v0.4
  * ``setCustomerBillingAgreement`` (pre 0.1.3 feature)
  * ``PAYPAL_RECEIVER_EMAIL`` (see notes under 0.3)
  * ``pdt`` view (see notes under 0.3)
  * ``sandbox`` method on forms (see notes under 0.2)


Version 0.5.0
-------------

* Dropped official support for Python 3.3

* Support for Django 2.0

* Fixed bug with IPv6 addresses (thanks @alexcrawley)

* Tidy up and update PayPalPaymentsForm. Specifically:

  * Where possible, remove explicit fields, leaving them to be handled by
    __init__(), which creates fields as required from the contents of ``initial``.

  * Deprecate field return_url - use field return instead. PayPal expects field
    ``return``, but Python's return keyword meant it wasn't possible to set that field in
    the class's definition. Later, code in __init__ was added to handle any value in ``initial``, in
    particular ``initial['return']``. As the work around which renamed 'return' to 'return_url'
    is not necessary, it is now being deprecated. To maintain backwards compatibility
    initial['return_url'] is remapped to initial['return'], with a deprecation warning.

    Thanks @JonathanRoach

  * Add cmd choices for _xclick-auto-billing and _xclick-payment-plan.

Version 0.4.1
-------------

* Added forgotten docs file

Version 0.4.0
-------------

* Cleaned up and documented all settings related to button images. Specifically:

  * The default images have been updated to recent ones. This is backwards
    incompatible if you were relying on the previous (very old) image and had
    not set ``PAYPAL_IMAGE`` in your settings.

  * Removed separate settings for sandbox mode - these only meant more work when
    configuring, and production looked different from sandbox by default. This
    is backwards incompatible, but only affects development mode.

  * Names of settings made clearer. The new names are:

    * ``PAYPAL_BUY_BUTTON_IMAGE`` (was: ``PAYPAL_IMAGE``)
    * ``PAYPAL_DONATION_BUTTON_IMAGE`` (was: ``PAYPAL_DONATION_IMAGE``)
    * ``PAYPAL_SUBSCRIPTION_BUTTON_IMAGE`` (was: ``PAYPAL_SUBSCRIPTION_IMAGE``)


Version 0.3.6
-------------

* Version bump due to messed up version numbers in previous release.

Version 0.3.4
-------------

* Use multi certificates with PaypalEncryptedPaymentsForm
* Fixed issue #166 - regression from 0.2.7 when using ``USE_TZ=False``
* Django 1.11 compatibility.
* Added warnings for untested code.

Version 0.3.3
-------------

* Fixed issue #147 - compatibility with Django 1.10

Version 0.3.2
-------------

* Fixed ``verify`` method of IPN/PDT so that it can be re-run in the case
  of a PayPal server error.
* Added 're-verify' admin action for IPNs.
* Other IPN admin improvements.
* *IMPORTANT:* Removed the undocumented and untested ``item_check_callable``
  parameter from several IPN and PDT processing functions. You should
  implement checks in signal handlers like ``valid_ipn_received`` or
  other calling code.
* Fixed issue #119 - flagged IPNs not excluded from duplicate checking.
* Fixed issue #126 - documented need to check amount received.

Version 0.3.1
-------------

* Better handling of unknown datetime formats, thanks rebwok, PR #137
* Added pytz dependency

Version 0.3
-----------

* Dropped support for Django 1.4 and 1.5.
* Fixed crasher with AmbiguousTimeError.
* Better logging for paypal.pro.
* Fixed Django 1.7/1.8 compat for EmailField.
* Added missing migration for PDT model.
* Added missing South migrations
* Fixed max_length of IPN/PDT ``custom`` and ``transaction_subject`` fields
* Fixed `issue #105
  <https://github.com/spookylukey/django-paypal/issues/105>`_ - IPN failure when
  running under non-English locale
* Added missing fields ``option_selection1`` and ``option_selection2`` to
  IPN/PDT

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

Regarding the handling of dates: If you want to fix historic data in your IPN
tables, you need to apply a migration like the following::

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals

    import pytz
    from datetime import datetime
    from django.db import migrations
    from django.utils import timezone


    PAYPAL_DATE_FORMATS = [
        "%H:%M:%S %b. %d, %Y PST",
        "%H:%M:%S %b. %d, %Y PDT",
        "%H:%M:%S %b %d, %Y PST",
        "%H:%M:%S %b %d, %Y PDT",
    ]


    def parse_date(datestring):
        for format in PAYPAL_DATE_FORMATS:
            try:
                return datetime.strptime(datestring, format)
            except (ValueError, TypeError):
                continue


    def fix_ipn_dates(apps, schema_editor):
        PayPalIPN = apps.get_model("ipn", "PayPalIPN")

        for ipn in PayPalIPN.objects.all():
            # Need to recreate PayPalIPN.posted_data_dict
            posted_data_dict = None
            if ipn.query:
                from django.http import QueryDict
                roughdecode = dict(item.split('=', 1) for item in ipn.query.split('&'))
                encoding = roughdecode.get('charset', None)
                if encoding is not None:
                    query = ipn.query.encode('ascii')
                    data = QueryDict(query, encoding=encoding)
                    posted_data_dict = data.dict()
            if posted_data_dict is None:
                continue

            for field in ['time_created', 'payment_date', 'next_payment_date', 'subscr_date', 'subscr_effective',
                          'retry_at', 'case_creation_date', 'auction_closing_date']:
                if field in posted_data_dict:
                    raw = posted_data_dict[field]
                    naive = parse_date(raw)
                    if naive is not None:
                        aware = timezone.make_aware(naive, pytz.timezone('US/Pacific'))
                        setattr(ipn, field, aware)
            ipn.save()


    class Migration(migrations.Migration):

        dependencies = [
            ('ipn', '0003_auto_20141117_1647'),
        ]

        operations = [
            migrations.RunPython(fix_ipn_dates,
                                 lambda apps, schema_editor: None)  # allowing reverse migration is harmless)
        ]


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

    Please see :doc:`standard/ipn`.

  * Pro:

    This used signals even though they weren't really appropriate.

    Instead:

    * If you are using ``PayPalWPP`` directly, the returned ``PayPalNVP`` objects
      from all method should just be used. Remember that you need to handle
      ``PayPalFailure`` exceptions from all direct calls.

    * If you are using the ``PayPalPro`` wrapper, you should pass a callable
      ``nvp_handler`` keyword argument.

    Please see :doc:`pro/index`.

* You must explicitly set ``PAYPAL_TEST`` to ``True`` or ``False`` in your
  settings, depending on whether you want production or sandbox PayPal. (The
  default is ``True`` i.e. sandbox mode).

  The ``sandbox()`` method on any forms is deprecated. You should use ``render``
  and set ``PAYPAL_TEST`` in your settings instead.


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



