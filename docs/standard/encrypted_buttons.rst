Using PayPal Standard with Encrypted Buttons
============================================

Use this method to encrypt your button so sneaky gits don't try to hack
it. Thanks to `Jon Atkinson <http://jonatkinson.co.uk/>`_ for the
`tutorial <http://jonatkinson.co.uk/paypal-encrypted-buttons-django/>`_.

1. Encrypted buttons require the `M2Crypto` library::

       pip install M2Crypto

2. Encrypted buttons require certificates. Create a private key::

       openssl genrsa -out paypal.pem 1024

3. Create a public key::

       openssl req -new -key paypal.pem -x509 -days 365 -out pubpaypal.pem

4. Upload your public key to the paypal website (sandbox or live).

   https://www.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert

   https://www.sandbox.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert

5. Copy your ``cert id`` - you'll need it in two steps. It's on the screen where
   you uploaded your public key.

6. Download PayPal's public certificate - it's also on that screen.

7. Edit your ``settings.py`` to include cert information:

   .. code-block:: python

       PAYPAL_PRIVATE_CERT = '/path/to/paypal.pem'
       PAYPAL_PUBLIC_CERT = '/path/to/pubpaypal.pem'
       PAYPAL_CERT = '/path/to/paypal_cert.pem'
       PAYPAL_CERT_ID = 'get-from-paypal-website'

8. Swap out your unencrypted button for a ``PayPalEncryptedPaymentsForm``:

   In views.py:

   .. code-block:: python

       from paypal.standard.forms import PayPalEncryptedPaymentsForm

       def view_that_asks_for_money(request):
           ...
           # Create the instance.
           form = PayPalPaymentsForm(initial=paypal_dict)
           # Works just like before!
           form.render()


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
