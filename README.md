Django PayPal
=============


About
-----

Django PayPal is a pluggable application that implements with PayPal Payments Standard and Payments Pro. It focused on selling software - think "Buy it Now" single items with no shipping or recurring payments.

Before diving in further a quick overview of PayPal's different payment methods might help. **[PayPal Payments Standard](https://cms.paypal.com/cms_content/US/en_US/files/developer/PP_WebsitePaymentsStandard_IntegrationGuide.pdf)** is the "Buy it Now" button you may have
seen floating around the internets. Buyers click on the button and are taken to PayPal's website where they can pay for the product. After completing the purchase PayPal makes an HTTP POST to your  `notify_url`. PayPal calls this process **[Instant Payment Notification](https://cms.paypal.com/cms_content/US/en_US/files/developer/PP_OrderMgmt_IntegrationGuide.pdf)** (IPN). Most people would agree that this method sucks (who wants to send people to PayPal's website)? But it is quick to implement and doesn't require any of your pages to use SSL.

**PayPal Payments Pro** allows you to accept payments on your website. It contains two payment flows - **Direct Payment** allows the user to enter credit card information on your website and pay on your website. **Express Checkout** sends the user over to PayPal to confirm their payment method before redirecting back to your website for confirmation. PayPal rules state that both methods must be implemented.


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

1.  Connect actions to the signals generated when PayPal talks to your `notify_url`.
    Currently there are two signals `payment_was_succesful` and `payment_was_flagged`.
    Both live in `paypal.standard.signals`. You can connect to either of these signals
    and update your data accordingly when payments are processed. [Django Signals Documentation](http://docs.djangoproject.com/en/dev/topics/signals/).

        # models.py (or somewhere)
        
        from paypal.standard.signals import payment_was_successful
        
        def show_me_the_money(sender, **kwargs):
            ipn_obj = sender
            # Undertake some action depending upon `ipn_obj`.
            if ipn_obj.cust == "Upgrade all users!":
                Users.objects.update(paid=True)        
        payment_was_successful.connect(show_me_the_money)

Using PayPal Payments Standard with Encrypted Buttons:
------------------------------------------------------

Use this method to encrypt your button so sneaky gits don't try to hack
it. Thanks to [Jon Atkinson](http://jonatkinson.co.uk/) for the [tutorial](http://jonatkinson.co.uk/paypal-encrypted-buttons-django/).

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
-------------------------------------------------------------------------

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


Using PayPal Payments Pro
-------------------------

PayPal Payments Pro is the more awesome version of PayPal that lets you accept payments on your site. Note that PayPal Pro uses a lot of the code from `paypal.standard` so you'll need to include both apps. Specifically IPN is still used for payment confirmation.

1. Edit `settings.py` and add  `paypal.standard` and `paypal.pro` to your `INSTALLED_APPS`:

        # settings.py
        ...
        INSTALLED_APPS = (... 'paypal.standard', 'paypal.pro', ...)

1. Write a view wrapper for `paypal.pro.views.PayPalPro` and add it to your `urls.py`:

        from paypal.pro.views import PayPalPro

        def buy_my_item(request):
            item = {'amt':"10.00",              # amount to charge for item
                    'inv':"inventory#",         # unique tracking variable paypal
                    'custom':"tracking#",       # custom tracking variable for you
                    'cancelurl':"http://...",   # Express checkout cancel url
                    'returnurl':"http://..."}   # Express checkout return url
        
        kw = {'item':'item',                            # what you're selling
               'payment_template': 'template',          # template to use for payment form
               'confirm_template': 'confirm_template',  # form class to use for Express checkout confirmation
               'payment_form_cls': 'payment_form_cls',  # form class to use for payment
               'success_url': '/success',               # where to redirect after successful payment
               }
        ppp = PayPalPro(**kw)
        return ppp(request)
        
        # urls.py
        
        urlpatterns = ('',
            ...
            (r'^payment-url/$', 'myproject.views.pro')
            ...
        )
        

1. Profit. (Setup NVP / IPN endpoints to receive information)
        

PayPal Initial Data:
--------------------

Typically you'll want to set these fields in your form...

Flags:
------

Flags are set on bad invalid transactions ...

ToDo:
=====

* Shared Secrets: I'm not master of encryption and the Shared Secrets implementation is just a stab in the dark. The implementation should be vetted before production use.

* Fixmes: Scattered throughout the code are triple hash ### FIXME comments with little actionable items.

* Testing: Not enough coverage.

* Query Fields: Lots of fields store QueryDict dumps b/c we're not sure exactly what we're getting - would be cool to be able to access those fields like they were a dict (JSONField)

* Feeds: Would also be awesome to have a feed of successful payments so you keep up to date with how rich you're getting.

Links:
------

1. [Set your IPN Endpoint on the PayPal Sandbox](https://www.sandbox.paypal.com/us/cgi-bin/webscr?cmd=_profile-ipn-notify)

License (MIT)
=============

Copyright (c) 2009 Handi Mobility Inc.

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.