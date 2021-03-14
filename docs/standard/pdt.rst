Using PayPal Standard PDT
=========================

Paypal Payment Data Transfer (PDT) allows you to display transaction details to
a customer immediately on return to your site unlike PayPal IPN which may take
some seconds. `You will need to enable PDT in your PayPal account to use it
<https://developer.paypal.com/webapps/developer/docs/classic/products/payment-data-transfer/>`_.

However, PDT also has the disadvantage that you only get one chance to handle
the notification - if there is a connection error for your user, the
notification will never arrive at your site. For this reason, using PDT with
django-paypal is not as well supported as IPN.

To use PDT:

1. Edit ``settings.py`` and add ``paypal.standard.pdt`` to your
   ``INSTALLED_APPS``. Also set ``PAYPAL_IDENTITY_TOKEN`` - you can find the
   correct value of this setting from the PayPal website:

   settings.py:

   .. code-block:: python

       #...
       INSTALLED_APPS = [
           #...
           'paypal.standard.pdt',
           #...
       ]

       #...

       PAYPAL_IDENTITY_TOKEN = "xxx"

   For installations on which you want to use the sandbox,
   set PAYPAL_TEST to True.  While testing, ensure that when you create
   the PayPalPaymentsForm your receiver email (`business` parameter) is set to
   your sandbox account email too.

2. :doc:`/updatedb`

3. Create a view that uses ``PayPalPaymentsForm`` just like in :doc:`ipn`.

4. After someone uses this button to buy something PayPal will return the user
   to your site at your ``return_url`` with some extra GET parameters.

   You will want to write a custom view that
   calls ``paypal.standard.pdt.views.process_pdt``. This function returns
   a tuple containing ``(PDT object, flag)``, where the ``flag`` is True
   if verification failed.

   Add the following to your `urls.py`:

   .. code-block:: python

       from django.urls import path, include
       ...
       urlpatterns = [
           path('your_return_url/', your_pdt_return_url_view, name="pdt_return_url"),
           ...
       ]


   And then create a view that uses the ``process_pdt`` helper function:

   .. code-block:: python

       @require_GET
       def your_pdt_return_url_view(request):
           pdt_obj, failed = process_pdt(request)
           context = {"failed": failed, "pdt_obj": pdt_obj}
           if not failed:

               # WARNING!
               # Check that the receiver email is the same we previously
               # set on the business field request. (The user could tamper
               # with those fields on payment form before send it to PayPal)

               if pdt_obj.receiver_email == "receiver_email@example.com":

                   # ALSO: for the same reason, you need to check the amount
                   # received etc. are all what you expect.

                   # Do whatever action is needed, then:
                   return render(request, 'my_valid_payment_template', context)
           return render(request, 'my_non_valid_payment_template', context)

   See the :doc:`variables` documentation for information about attributes on
   the PDT object that you can use.
