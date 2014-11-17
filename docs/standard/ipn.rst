Using PayPal Standard IPN
=========================

1. Edit `settings.py` and add  `paypal.standard.ipn` to your `INSTALLED_APPS`
   and `PAYPAL_RECEIVER_EMAIL`:

   settings.py:

   .. code-block:: python

       #...

       INSTALLED_APPS = [
           #...
           'paypal.standard.ipn',
           #...
       ]

       #...
       PAYPAL_RECEIVER_EMAIL = "yourpaypalemail@example.com"

   For installations on which you want to use the sandbox,
   set PAYPAL_TEST to True.  Ensure PAYPAL_RECEIVER_EMAIL is set to
   your sandbox account email too.

2. Create an instance of the `PayPalPaymentsForm` in the view where you would
   like to collect money. Call `render` on the instance in your template to
   write out the HTML.

   views.py:

   .. code-block:: python

       from paypal.standard.forms import PayPalPaymentsForm

       def view_that_asks_for_money(request):

           # What you want the button to do.
           paypal_dict = {
               "business": settings.PAYPAL_RECEIVER_EMAIL,
               "amount": "10000000.00",
               "item_name": "name of the item",
               "invoice": "unique-invoice-id",
               "notify_url": "https://www.example.com" + reverse('paypal-ipn'),
               "return_url": "https://www.example.com/your-return-location/",
               "cancel_return": "https://www.example.com/your-cancel-location/",

           }

           # Create the instance.
           form = PayPalPaymentsForm(initial=paypal_dict)
           context = {"form": form}
           return render_to_response("payment.html", context)

   For a full list of variables that can be used in ``paypal_dict``, see
   `PayPal HTML variables documentation" <https://developer.paypal.com/webapps/developer/docs/classic/paypal-payments-standard/integration-guide/Appx_websitestandard_htmlvariables/>`_


   payment.html:

   .. code-block:: html

       ...
       <h1>Show me the money!</h1>
       <!-- writes out the form tag automatically -->
       {{ form.render }}


3. When someone uses this button to buy something PayPal makes a HTTP POST to
   your "notify_url". PayPal calls this Instant Payment Notification (IPN).
   The view ``paypal.standard.ipn.views.ipn`` handles IPN processing. To set the
   correct ``notify_url`` add the following to your ``urls.py``:

   .. code-block:: python

       urlpatterns = patterns('',
           (r'^something/paypal/', include('paypal.standard.ipn.urls')),
       )

4. Whenever an IPN is processed a signal will be sent with the result of the
   transaction. Connect the signals to actions to perform the needed operations
   when a successful payment is received.

   The IPN signals should be imported from ``paypal.standard.ipn.signals``.

   There are four signals for basic transactions:

   * ``payment_was_successful``
   * ``payment_was_flagged``
   * ``payment_was_refunded``
   * ``payment_was_reversed``

   And four signals for subscriptions:

   * ``subscription_cancel`` - Sent when a subscription is cancelled.
   * ``subscription_eot`` - Sent when a subscription expires.
   * ``subscription_modify`` - Sent when a subscription is modified.
   * ``subscription_signup`` - Sent when a subscription is created.

   Several more exist for recurring payments:

   * ``recurring_create`` - Sent when a recurring payment is created.
   * ``recurring_payment`` - Sent when a payment is received from a recurring payment.
   * ``recurring_cancel`` - Sent when a recurring payment is cancelled.
   * ``recurring_suspend`` - Sent when a recurring payment is suspended.
   * ``recurring_reactivate`` - Sent when a recurring payment is reactivated.

   Connect to these signals and update your data accordingly.  `Django Signals
   Documentation <http://docs.djangoproject.com/en/dev/topics/signals/>`_.

   models.py:

   .. code-block:: python

       from paypal.standard.ipn.signals import payment_was_successful

       def show_me_the_money(sender, **kwargs):
           ipn_obj = sender
           # You need to check 'payment_status' of the IPN

           if ipn_obj.payment_status == "Completed":
               # Undertake some action depending upon `ipn_obj`.
               if ipn_obj.custom == "Upgrade all users!":
                   Users.objects.update(paid=True)
           else:
               #...

       payment_was_successful.connect(show_me_the_money)

   The data variables that are return on the IPN object are documented here:

   https://developer.paypal.com/webapps/developer/docs/classic/ipn/integration-guide/IPNandPDTVariables/

   You need to pay particular attention to ``payment_status``.

5. You will also need to implement the ``return_url`` and ``cancel_return`` views
   to handle someone returning from PayPal. Note that these views need
   ``@csrf_exempt`` applied to them, because PayPal will POST to them, so they
   should be custom views that don't need to handle POSTs otherwise.

   For 'return_url' you need to cope with the possibility that the IPN has not
   yet been received and handled by the IPN listener you implemented (which can
   happen rarely), or that there was some kind of error with the IPN.

See also
--------

* :doc:`subscriptions`
* :doc:`encrypted_buttons`

