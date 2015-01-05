Release notes
=============

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
