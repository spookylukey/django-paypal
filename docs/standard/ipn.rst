Using PayPal Standard IPN
=========================

1. Edit ``settings.py`` and add ``paypal.standard.ipn`` to your ``INSTALLED_APPS``:

   ``settings.py``:

   .. code-block:: python

       #...

       INSTALLED_APPS = [
           #...
           'paypal.standard.ipn',
           #...
       ]


   For installations on which you want to use the sandbox,
   set PAYPAL_TEST to True.

   .. code-block:: python

       PAYPAL_TEST = True



2. :doc:`/updatedb`

3. Create an instance of the ``PayPalPaymentsForm`` in the view where you would
   like to collect money.

   You must fill a dictionary with the information required to complete the
   payment, and pass it through the ``initial`` parameter when creating the
   ``PayPalPaymentsForm``.

   Please note: **This form is not used like a normal Django form** that posts
   back to a Django view. Rather it is a GET form that has a single button
   which sends all the data to PayPal. You simply need to call ``render``
   on the instance in your template to write out the HTML, which includes
   the ``<form>`` tag with the correct endpoint.

   ``views.py``:

   .. code-block:: python

       from django.core.urlresolvers import reverse
       from django.shortcuts import render
       from paypal.standard.forms import PayPalPaymentsForm

       def view_that_asks_for_money(request):

           # What you want the button to do.
           paypal_dict = {
               "business": "receiver_email@example.com",
               "amount": "10000000.00",
               "item_name": "name of the item",
               "invoice": "unique-invoice-id",
               "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
               "return": request.build_absolute_uri(reverse('your-return-view')),
               "cancel_return": request.build_absolute_uri(reverse('your-cancel-view')),
               "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
           }

           # Create the instance.
           form = PayPalPaymentsForm(initial=paypal_dict)
           context = {"form": form}
           return render(request, "payment.html", context)


   For a full list of variables that can be used in ``paypal_dict``, see
   `PayPal HTML variables documentation <https://developer.paypal.com/webapps/developer/docs/classic/paypal-payments-standard/integration-guide/Appx_websitestandard_htmlvariables/>`_.

   .. note:: The names of these variables are not the same as the values
             returned on the IPN object.

   ``payment.html``:

   .. code-block:: html

       ...
       <h1>Show me the money!</h1>
       <!-- writes out the form tag automatically -->
       {{ form.render }}

   The image used for the button can be customized using the :doc:`/settings`, or
   by subclassing ``PayPalPaymentsForm`` and overriding the ``get_image``
   method.

4. When someone uses this button to buy something PayPal makes a HTTP POST to
   your "notify_url". PayPal calls this Instant Payment Notification (IPN).
   The view ``paypal.standard.ipn.views.ipn`` handles IPN processing. To set the
   correct ``notify_url`` add the following to your ``urls.py``:

   .. code-block:: python

       from django.conf.urls import url, include

       urlpatterns = [
           url(r'^paypal/', include('paypal.standard.ipn.urls')),
       ]

5. Whenever an IPN is processed a signal will be sent with the result of the
   transaction.

   The IPN signals should be imported from ``paypal.standard.ipn.signals``. They
   are:

   * ``valid_ipn_received``

     This indicates a correct, non-duplicate IPN message from PayPal. The
     handler will receive a :class:`paypal.standard.ipn.models.PayPalIPN` object
     as the sender. You will need to check the ``payment_status`` attribute, and
     the ``business`` to make sure that the account receiving the payment
     is the expected one, as well as other attributes to know what action to
     take.

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


   Example code: ``yourproject/hooks.py``

   .. code-block:: python

       from paypal.standard.models import ST_PP_COMPLETED
       from paypal.standard.ipn.signals import valid_ipn_received

       def show_me_the_money(sender, **kwargs):
           ipn_obj = sender
           if ipn_obj.payment_status == ST_PP_COMPLETED:
               # WARNING !
               # Check that the receiver email is the same we previously
               # set on the `business` field. (The user could tamper with
               # that fields on the payment form before it goes to PayPal)
               if ipn_obj.receiver_email != "receiver_email@example.com":
                   # Not a valid payment
                   return

               # ALSO: for the same reason, you need to check the amount
               # received, `custom` etc. are all what you expect or what
               # is allowed.

               # Undertake some action depending upon `ipn_obj`.
               if ipn_obj.custom == "premium_plan":
                   price = ...
               else:
                   price = ...

               if ipn_obj.mc_gross == price and ipn_obj.mc_currency == 'USD':
                   ...
           else:
               #...

       valid_ipn_received.connect(show_me_the_money)

   Remember to ensure that import the hooks file is imported i.e. that you are
   connecting the signals when your project initializes. The standard way to do
   this is to `create an AppConfig class
   <https://docs.djangoproject.com/en/2.1/ref/applications/#configuring-applications>`_
   and add a `ready()
   <https://docs.djangoproject.com/en/2.1/ref/applications/#django.apps.AppConfig.ready>`_
   method, in which you can register your signal handlers or import a module
   that does this.

   See the :doc:`variables` documentation for information about attributes on
   the IPN object that you can use.

6. You will also need to implement the ``return`` and ``cancel_return`` views
   to handle someone returning from PayPal.

   Note that the ``return`` view may need ``@csrf_exempt`` applied to it,
   because PayPal may POST to it (depending on the value of the
   `rm parameter <https://developer.paypal.com/webapps/developer/docs/classic/paypal-payments-standard/integration-guide/Appx_websitestandard_htmlvariables/#paypal-checkout-page-variables>`_
   and possibly other settings), so it should be a custom view that doesn't need
   to handle POSTs otherwise.

   When using PayPal Standard with Subscriptions this is not necessary since
   PayPal will route the user back to your site via GET.

   For ``return``, you need to cope with the possibility that the IPN has not
   yet been received and handled by the IPN listener you implemented (which can
   happen rarely), or that there was some kind of error with the IPN.


Testing
-------

If you are attempting to test this in development, using the PayPal sandbox, and
your machine is behind a firewall/router and therefore is not publicly
accessible on the internet (this will be the case for most developer machines),
PayPal will not be able to post back to your view. You will need to use a tool
like https://ngrok.com/ to make your machine publicly accessible, and ensure
that you are sending PayPal your public URL, not ``localhost``, in the
``notify_url``, ``return`` and ``cancel_return`` fields.

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
