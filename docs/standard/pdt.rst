Using PayPal Standard PDT
=========================

Paypal Payment Data Transfer (PDT) allows you to display transaction details to
a customer immediately on return to your site unlike PayPal IPN which may take
some seconds. `You will need to enable PDT in your PayPal account to use it
<https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/howto_html_paymentdatatransfer>`_.

However, PDT also has the disadvantage that you only get one chance to handle
the notification - if there is a connection error for your user, the
notification will never arrive at your site. For this reason, using PDT with
django-paypal is not as well supported as IPN.

To use PDT:

1. Edit `settings.py` and add  `paypal.standard.pdt` to your `INSTALLED_APPS`. Also set `PAYPAL_IDENTITY_TOKEN` - you can find the correct value of this setting from the PayPal website:

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
   set PAYPAL_TEST to True.  Ensure PAYPAL_RECEIVER_EMAIL is set to
   your sandbox account email too.

2. :doc:`/updatedb`

3. Create a view that uses `PayPalPaymentsForm` just like in :doc:`ipn`.

4. After someone uses this button to buy something PayPal will return the user
   to your site at your ``return_url`` with some extra GET parameters.

   The view ``paypal.standard.pdt.views.pdt`` handles PDT processing and renders
   a simple template. It can be used as follows:


   Add the following to your `urls.py`:

   .. code-block:: python

       from django.conf.urls import url, include
       ...
       urlpatterns = [
           url(r'^paypal/pdt/', include('paypal.standard.pdt.urls')),
           ...
       ]

   Then specify the ``return_url`` to use this URL.

   You will also need to have a ``base.html`` template with a block
   ``content``. This template is inherited by the PDT view template.

   More than likely, however, you will want to write a custom view that
   calls ``paypal.standard.pdt.views.process_pdt``. This function returns
   a tuple containing ``(PDT object, flag)``, where the ``flag`` is True
   if verification failed.
