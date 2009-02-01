Django PayPal
=============


About
-----

Django PayPal is a pluggable application that implements with PayPal Payments Standard and Payments Pro. It focused on selling software - think "Buy it Now" single items with no shipping.

Before diving in further a quick overview of PayPal's different payment methods might help. **[PayPal Payments Standard](https://cms.paypal.com/cms_content/US/en_US/files/developer/PP_WebsitePaymentsStandard_IntegrationGuide.pdf)** is the "Buy it Now" button you may have
seen floating around the internets. Buyers click on the button and are taken to PayPal's website where they can pay for the product. After completing the purchase PayPal makes an HTTP POST to your  `notify_url`. PayPal calls this process **[Instant Payment Notification](https://cms.paypal.com/cms_content/US/en_US/files/developer/PP_OrderMgmt_IntegrationGuide.pdf)** (IPN). Most people would agree that this method sucks (who wants to send people to PayPal's website)? But it is quick to implement and doesn't require any of your pages to use SSL.

**PayPal Payments Pro** allows you to accept payments on your website (though you still have to provide functionality to buy through PayPal : \)... and is currently under development.

Usage:
------

1. Download the code from GitHub:

        git clone git://github.com/johnboxall/django-paypal.git paypal
    
1. Edit `settings.py` and add  `paypal.standard` or `paypal.pro` to your `INSTALLED_APPS`:

        # settings.py
        ...
        INSTALLED_APPS = (... 'paypal.standard', ...)

Using PayPal Payments Standard:
-------------------------------

1.  First create an instance of the `PayPalPaymentsForm` in a view. 
    Call `render` on the instance to write out the HTML for the button.

        # views.py
        ...
        from paypal.standard.forms import PayPalPaymentsForm
        
        def view_that_asks_for_money(request):
        
            # What you want the button to do.
            paypal_dict = {
                "business": "yourpaypalemail@example.com",
                "amount": "100000.00",
                "item_name": "name of the item",
                "invoice": "unique-invoice-id",
                "notify_url": "http://www.example.com/your-ipn-location/",
                "return_url": "http://www.example.com/your-return-location/",
                "cancel_return": "http://www.example.com/your-cancel-location/",
            
            }
            
            # Create the instance.
            form = PayPalPaymentsForm(initial=paypal_dict)
            
            # Output the button.
            form.render()

1.  When someone uses this button to buy something PayPal makes a HTTP POST to 
    your "notify_url". PayPal calls this Instant Payment Notification (IPN). 
    The view `paypal.standard.views.ipn` handles IPN processing. Make sure it 
    is the same as the `notify_url` you specified in `paypal_dict` above then add 
    it to your `urls.py`:

        # urls.py
        ...
        urlpatterns = patterns('',
            (r'^ipn/$', 'paypal.standard.views.ipn'),
            ...
        )

Using PayPal Payments Standard with Encrypted Buttons:
------------------------------------------------------

Use this method to encrypt your button so sneaky gits don't try to hack
it. Thanks [Jon Atkinson](http://jonatkinson.co.uk/) [tutorial](http://jonatkinson.co.uk/paypal-encrypted-buttons-django/).

1. Encrypted buttons require the `M2Crypto` library:

        easy_install M2Crypto
    

1. Encrypted buttons require certificates. Create a private key:

        openssl genrsa -out paypal.pem 1024

1. Create a public key:

        openssl req -new -key paypal.pem -x509 -days 365 -out pubpaypal.pem

1. Upload your public key to the paypal website (sandbox or live).
        
    [https://www.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert](https://www.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert)

    [https://www.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert](https://www.sandbox.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert)

1.  Copy your `cert id` - you'll need it in two steps. It's on the screen where
    you uploaded your public key.

1. Download PayPal's public certificate - it's also on that screen.

1. Edit your `settings.py` to include cert information:

        # settings.py
        PAYPAL_PRIVATE_CERT = '/path/to/paypal.pem'
        PAYPAL_PUBLIC_CERT = '/path/to/pubpaypal.pem'
        PAYPAL_CERT = '/path/to/paypal_cert.pem'
        PAYPAL_CERT_ID = 'get-from-paypal-website'

1. Swap out your unencrypted button for a `PayPalEncryptedPaymentsForm`:

        # views.py
        from paypal.standard.forms import PayPalEncryptedPaymentsForm
        
        def view_that_asks_for_money(request):
            ...
            # Create the instance.
            form = PayPalPaymentsForm(initial=paypal_dict)
            # Works just like before!
            form.render()


Using PayPal Payments Standard with Encrypted Buttons and Shared Secrets:
------------------------------------------------------

This method uses Shared secrets instead of IPN postback to verify that transactions
are legit. PayPal recommends you should use Shared Secrets if:

    * You are not using a shared website hosting service. 
    * You have enabled SSL on your web server. 
    * You are using Encrypted Website Payments. 
    * You use the notify_url variable on each individual payment transaction.
    
Use postbacks for validation if: 
    * You rely on a shared website hosting service 
    * You do not have SSL enabled on your web server 

1. Swap out your button for a `PayPalSharedSecretEncryptedPaymentsForm`:

        # views.py
        from paypal.standard.forms import PayPalSharedSecretEncryptedPaymentsForm
        
        def view_that_asks_for_money(request):
            ...
            # Create the instance.
            form = PayPalSharedSecretEncryptedPaymentsForm(initial=paypal_dict)
            # Works just like before!
            form.render()
            
1. Verify that your IPN endpoint is running on SSL - request.is_secure() should return True!

-------------------

PayPal Initial Data:
--------------------

Typically you'll want to set these fields in your form...

Flags:
------

Flags are set on bad invalid transactions ...


-------------------

ToDo:
=====

*   I'm not master of encryption and the Shared Secrets implementation is just a stab in the dark. The implementation should be vetted before production use.

* Scattered throughout the code are triple hash ### ToDo comments with little actionable items.

* PayPal payments pro is in the works.

* IPN created should probably emit signals so that other objects can update themselves on the correct conditions.

* TESTS. Yah, this needs some test scripts bad...