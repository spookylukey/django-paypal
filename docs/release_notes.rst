Release notes
=============

Version 0.2.4/0.2.5
-------------------

This fixes a bug with handling of dates. If you want to fix historic data in
your IPN tables, you need to apply a migration like the following::

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

    * If you are using `PayPalWPP` directly, the returned `PayPalNVP` objects
      from all method should just be used. Remember that you need to handle
      `PayPalFailure` exceptions from all direct calls.

    * If you are using the `PayPalPro` wrapper, you should pass a callable
      `nvp_handler` keyword argument.

    Please see :doc:`pro/index`.

* You must explicitly set ``PAYPAL_TEST`` to ``True`` or ``False`` in your
  settings, depending on whether you want production or sandbox PayPal. (The
  default is ``True`` i.e. sandbox mode).

  The ``sandbox()`` method on any forms is deprecated. You should use ``render``
  and set ``PAYPAL_TEST`` in your settings instead.
