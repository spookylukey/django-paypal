Using PayPal Standard IPN
=========================

1. Edit ``settings.py`` and add ``paypal.standard.ipn`` to your ``INSTALLED_APPS``
   and ``PAYPAL_RECEIVER_EMAIL``:

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

2. :doc:`/updatedb`

3. Create an instance of the ``PayPalPaymentsForm`` in the view where you would
   like to collect money. Call ``render`` on the instance in your template to
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
           return render(request, "payment.html", context)

   For a full list of variables that can be used in ``paypal_dict``, see
   `PayPal HTML variables documentation <https://developer.paypal.com/webapps/developer/docs/classic/paypal-payments-standard/integration-guide/Appx_websitestandard_htmlvariables/>`_.


   payment.html:

   .. code-block:: html

       ...
       <h1>Show me the money!</h1>
       <!-- writes out the form tag automatically -->
       {{ form.render }}


4. When someone uses this button to buy something PayPal makes a HTTP POST to
   your "notify_url". PayPal calls this Instant Payment Notification (IPN).
   The view ``paypal.standard.ipn.views.ipn`` handles IPN processing. To set the
   correct ``notify_url`` add the following to your ``urls.py``:

   .. code-block:: python

       from django.conf.urls import url, include

       urlpatterns = [
           url(r'^something/paypal/', include('paypal.standard.ipn.urls')),
       ]

5. Whenever an IPN is processed a signal will be sent with the result of the
   transaction.

   The IPN signals should be imported from ``paypal.standard.ipn.signals``. They
   are:

   * ``valid_ipn_received``

     This indicates a correct, non-duplicate IPN message from PayPal. The
     handler will receive a :class:`paypal.standard.ipn.models.PayPalIPN` object
     as the sender. You will need to check the ``payment_status`` attribute and
     other attributes to know what action to take.

   * ``invalid_ipn_received``

     This is sent when a transaction was flagged - because of a failed check
     with PayPal, for example, or a duplicate transaction ID. You should never
     act on these, but might want to be notified of a problem.

   Connect the signals to actions to perform the needed operations
   when a successful payment is received (as described in the `Django Signals
   Documentation <http://docs.djangoproject.com/en/dev/topics/signals/>`_).

   In the past there were more specific signals, but they were named
   confusingly, and used inconsistently, and are now deprecated. (`See v0.1.5
   docs for details
   <http://django-paypal.readthedocs.org/en/v0.1.5/standard/ipn.html>`_)


   Example code:

   .. code-block:: python

       from paypal.standard.models import ST_PP_COMPLETED
       from paypal.standard.ipn.signals import valid_ipn_received

       def show_me_the_money(sender, **kwargs):
           ipn_obj = sender
           if ipn_obj.payment_status == ST_PP_COMPLETED:
               # Undertake some action depending upon `ipn_obj`.
               if ipn_obj.custom == "Upgrade all users!":
                   Users.objects.update(paid=True)
           else:
               #...

       valid_ipn_received.connect(show_me_the_money)

   The data variables that are returned on the IPN object are documented here:

   https://developer.paypal.com/webapps/developer/docs/classic/ipn/integration-guide/IPNandPDTVariables/

   You need to pay particular attention to ``payment_status`` (`docs
   <https://developer.paypal.com/webapps/developer/docs/classic/ipn/integration-guide/IPNandPDTVariables/#id091EB04C0HS__id0913D0E0UQU>`_). Use
   can use the ``ST_PP_*`` constants in ``paypal.standard.models`` to help.

6. You will also need to implement the ``return_url`` and ``cancel_return`` views
   to handle someone returning from PayPal. Note that these views need
   ``@csrf_exempt`` applied to them, because PayPal will POST to them, so they
   should be custom views that don't need to handle POSTs otherwise.

   For ``return_url``, you need to cope with the possibility that the IPN has not
   yet been received and handled by the IPN listener you implemented (which can
   happen rarely), or that there was some kind of error with the IPN.


Testing
-------

If you are attempting to test this in development, using the PayPal sandbox, and
your machine is behind a firewall/router and therefore is not publicly
accessible on the internet (this will be the case for most developer machines),
PayPal will not be able to post back to your view. You will need to use a tool
like https://ngrok.com/ to make your machine publicly accessible, and ensure
that you are sending PayPal your public URL, not ``localhost``.

Simulator testing
-----------------

The PayPal IPN simulator at https://developer.paypal.com/developer/ipnSimulator
has some unfortunate bugs:

* it doesn't send the ``encoding`` parameter. django-paypal deals with this
  using a guess.

* the default 'payment_date' that is created for you is in the wrong format. You
  need to change it to something like::

    23:04:06 Feb 02, 2015 PDT


See also
--------

* :doc:`subscriptions`
* :doc:`encrypted_buttons`

