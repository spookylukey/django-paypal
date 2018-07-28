Using PayPal Standard with Encrypted Buttons
============================================

Use this method to encrypt your button so values in the form can't be tampered
with. Thanks to `Jon Atkinson <http://jonatkinson.co.uk/>`_ for the `tutorial
<http://jonatkinson.co.uk/paypal-encrypted-buttons-django/>`_.

1. Encrypted buttons require the `M2Crypto` library::

       pip install M2Crypto


2. Encrypted buttons require certificates. Create a private key::

       openssl genrsa -out paypal_private.pem 1024

3. Create a public key::

       openssl req -new -key paypal_private.pem -x509 -days 365 -out paypal_public.pem

4. Upload your public key to the paypal website (sandbox or live).

   https://www.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert

   https://www.sandbox.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert

5. Copy your ``cert id`` - you'll need it in two steps. It's on the screen where
   you uploaded your public key.

6. Download PayPal's public certificate - it's also on that screen.

7. Edit your ``settings.py`` to include cert information:

   .. code-block:: python

       PAYPAL_PRIVATE_CERT = '/path/to/paypal_private.pem'
       PAYPAL_PUBLIC_CERT = '/path/to/paypal_public.pem'
       PAYPAL_CERT = '/path/to/paypal_cert.pem'
       PAYPAL_CERT_ID = 'get-from-paypal-website'

8. Swap out your unencrypted button for a ``PayPalEncryptedPaymentsForm``:

   In views.py:

   .. code-block:: python

       from paypal.standard.forms import PayPalEncryptedPaymentsForm

       def view_that_asks_for_money(request):
           ...
           # Create the instance.
           form = PayPalEncryptedPaymentsForm(initial=paypal_dict)
           # Works just like before!
           form.render()

9. If you need to use multiple certificates, you can pass
   the arguments directly to the PayPalEncryptedPaymentsForm
   as below:

   In views.py:

   .. code-block:: python

       from paypal.standard.forms import PayPalEncryptedPaymentsForm

       def view_that_asks_for_money(request):
           ...
           # Paypal Certificate Information
           paypal_private_cert = '/path/to/another/paypal_private.pem'
           paypal_public_cert = '/path/to/another/paypal_public.pem'
           paypal_cert = '/path/to/another/paypal_cert.pem'
           paypal_cert_id = 'another-paypal-id'
           # Create the instance.
           form = PayPalEncryptedPaymentsForm(initial=paypal_dict,
                private_cert=paypal_private_cert,
                public_cert=paypal_public_cert,
                paypal_cert=paypal_cert,
                cert_id=paypal_cert_id)
           ...


Using PayPal Payments Standard with Encrypted Buttons and Shared Secrets
------------------------------------------------------------------------

This method uses Shared secrets instead of IPN postback to verify that transactions
are legit. PayPal recommends you should use Shared Secrets if:

* You are not using a shared website hosting service.
* You have enabled SSL on your web server.
* You are using Encrypted Website Payments.
* You use the ``notify_url`` variable on each individual payment transaction.

Use postbacks for validation if:

* You rely on a shared website hosting service
* You do not have SSL enabled on your web server

1. Swap out your button for a ``PayPalSharedSecretEncryptedPaymentsForm``:


   In views.py:

   .. code-block:: python

       from paypal.standard.forms import PayPalSharedSecretEncryptedPaymentsForm

       def view_that_asks_for_money(request):
           ...
           # Create the instance.
           form = PayPalSharedSecretEncryptedPaymentsForm(initial=paypal_dict)
           # Works just like before!
           form.render()

2. Verify that your IPN endpoint is running on SSL - ``request.is_secure()`` should return ``True``!
