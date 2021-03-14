Using Website Payments Pro
==========================


.. toctree::
   :maxdepth: 2

   detail


`Website Payments Pro
<https://developer.paypal.com/docs/classic/products/website-payments-pro/>`_ is
a version of PayPal that lets you accept payments on your site using server side
calls. The branding of this is confusing. It was branded as "Paypal Payments
Pro" at one point. Later "PayPal Payments Pro (Payflow Edition)" was introduced,
and that was later renamed to "PayPal Payments Pro", while the old "PayPal
Payments Pro" was rebranded to "Website Payments Pro". It is this older API (not
Payflow) that is supported by django-paypal and documented here.

The PayPal Website Payments Pro solution reuses code from `paypal.standard` so
you'll need to include both apps. django-paypal makes the whole process
incredibly easy to use through the provided ``PayPalPro`` class.

1. Obtain PayPal Pro API credentials: login to PayPal, click *My Account*,
   *Profile*, *Request API credentials*, *Set up PayPal API credentials and
   permissions*, *View API Signature*.

2. Edit ``settings.py`` and add  ``paypal.standard`` and ``paypal.pro`` to your
   ``INSTALLED_APPS`` and put in your PayPal Pro API credentials.

   .. code-block:: python

       INSTALLED_APPS = [
           # ..
           'paypal.standard',
           'paypal.pro',
       ]
       PAYPAL_TEST = True
       PAYPAL_WPP_USER = "???"
       PAYPAL_WPP_PASSWORD = "???"
       PAYPAL_WPP_SIGNATURE = "???"

3. :doc:`/updatedb`

4. Write a wrapper view for ``paypal.pro.views.PayPalPro``:


   In views.py:

   .. code-block:: python

       from paypal.pro.views import PayPalPro

       def nvp_handler(nvp):
           # This is passed a PayPalNVP object when payment succeeds.
           # This should do something useful!
           pass

       def buy_my_item(request):
           item = {"paymentrequest_0_amt": "10.00",  # amount to charge for item
                   "inv": "inventory",         # unique tracking variable paypal
                   "custom": "tracking",       # custom tracking variable for you
                   "cancelurl": "http://...",  # Express checkout cancel url
                   "returnurl": "http://..."}  # Express checkout return url

           ppp = PayPalPro(
                     item=item,                            # what you're selling
                     payment_template="payment.html",      # template name for payment
                     confirm_template="confirmation.html", # template name for confirmation
                     success_url="/success/",              # redirect location after success
                     nvp_handler=nvp_handler)
           return ppp(request)

5. Create templates for payment and confirmation. By default both templates are
   populated with the context variable ``form`` which contains either a
   ``PaymentForm`` or a ``Confirmation`` form.


   payment.html:

   .. code-block:: html

       <h1>Show me the money</h1>
       <form method="post" action="">
         {{ form }}
         <input type="submit" value="Pay Up">
       </form>

   confirmation.html:

   .. code-block:: html

       <!-- confirmation.html -->
       <h1>Are you sure you want to buy this thing?</h1>
       <form method="post" action="">
         {{ form }}
         <input type="submit" value="Yes I Yams">
       </form>

6. Add your view to ``urls.py``, and add the IPN endpoint to receive callbacks
   from PayPal:

   .. code-block:: python

       from django.urls import path, include

       from myproject import views


       urlpatterns = [
           ...
           path('payment-url/', views.buy_my_item),
           path('paypal/', include('paypal.standard.ipn.urls')),
       ]

7. Profit.

Alternatively, if you want to get down to the nitty gritty and perform some
more advanced operations with Payments Pro, use the :class:`paypal.pro.helpers.PayPalWPP` class directly.

If you are testing locally using the WPP sandbox and are having SSL
problems, please see `issue 145
<https://github.com/spookylukey/django-paypal/issues/145>`_.
