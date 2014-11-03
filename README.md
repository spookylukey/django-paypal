Django PayPal
=============


About
-----

Django PayPal is a pluggable application that implements with PayPal Payments
Standard and Payments Pro.

Before diving in, a quick review of PayPal's payment methods is in order!
[PayPal Payments Standard](https://developer.paypal.com/webapps/developer/docs/classic/paypal-payments-standard/integration-guide/wp_standard_overview/)
is the "Buy it Now" buttons you may have seen floating around the
internets. Buyers click on the button and are taken to PayPal's website where
they can pay for the product. After completing the purchase PayPal makes an HTTP
POST to your `notify_url`. PayPal calls this process [Instant Payment
Notification](https://cms.paypal.com/cms_content/US/en_US/files/developer/PP_OrderMgmt_IntegrationGuide.pdf)
(IPN) but you may know it as [webhooks](http://www.webhooks.org/). This method
kinda sucks because it drops your customers off at PayPal's website but it's
easy to implement and doesn't require SSL.

PayPal Payments Pro allows you to accept payments on your website. It contains
two distinct payment flows - Direct Payment allows the user to enter credit card
information on your website and pay on your website. Express Checkout sends the
user over to PayPal to confirm their payment method before redirecting back to
your website for confirmation. PayPal rules state that both methods must be
implemented.

More recently, PayPal have implemented newer APIs, including "PayPal Payments
Pro (Payflow Edition)". This is not to be confused with the "Classic" PayPal
Payments Pro that is implemented by django-paypal. "Payflow Edition" is not yet
supported by django-paypal.


Using PayPal Payments Standard IPN:
-----------------------------------

1. Download the code from GitHub:

        git clone git://github.com/spookylukey/django-paypal.git paypal

1. Edit `settings.py` and add  `paypal.standard.ipn` to your `INSTALLED_APPS`
   and `PAYPAL_RECEIVER_EMAIL`:

        # settings.py
        ...
        INSTALLED_APPS = (... 'paypal.standard.ipn', ...)
        ...
        PAYPAL_RECEIVER_EMAIL = "yourpaypalemail@example.com"

        # For installations on which you want to use the sandbox,
        # set PAYPAL_TEST to True.  Ensure PAYPAL_RECEIVER_EMAIL is set to
        # your sandbox account email too.
        # PAYPAL_TEST = True

1. Create an instance of the `PayPalPaymentsForm` in the view where you would
   like to collect money. Call `render` on the instance in your template to
   write out the HTML.

        # views.py
        ...
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


        <!-- payment.html -->
        ...
        <h1>Show me the money!</h1>
        <!-- writes out the form tag automatically -->
        {{ form.render }}

    For a full list of variables that can be used in `paypal_dict`, see
    [PayPal HTML variables documentation][paypalhtml].

1. When someone uses this button to buy something PayPal makes a HTTP POST to
   your "notify_url". PayPal calls this Instant Payment Notification (IPN).
   The view `paypal.standard.ipn.views.ipn` handles IPN processing. To set the
   correct `notify_url` add the following to your `urls.py`:

        # urls.py
        ...
        urlpatterns = patterns('',
            (r'^something/paypal/', include('paypal.standard.ipn.urls')),
        )

1. Whenever an IPN is processed a signal will be sent with the result of the
   transaction. Connect the signals to actions to perform the needed operations
   when a successful payment is received.

   There are four signals for basic transactions:
   - `payment_was_successful`
   - `payment_was_flagged`
   - `payment_was_refunded`
   - `payment_was_reversed`

   And four signals for subscriptions:
   - `subscription_cancel` - Sent when a subscription is cancelled.
   - `subscription_eot` - Sent when a subscription expires.
   - `subscription_modify` - Sent when a subscription is modified.
   - `subscription_signup` - Sent when a subscription is created.

   Several more exist for recurring payments:
   - `recurring_create` - Sent when a recurring payment is created.
   - `recurring_payment` - Sent when a payment is received from a recurring payment.
   - `recurring_cancel` - Sent when a recurring payment is cancelled.
   - `recurring_suspend` - Sent when a recurring payment is suspended.
   - `recurring_reactivate` - Sent when a recurring payment is reactivated.

   Connect to these signals and update your data accordingly.
   [Django Signals Documentation](http://docs.djangoproject.com/en/dev/topics/signals/).

   models.py:

        from paypal.standard.ipn.signals import payment_was_successful

        def show_me_the_money(sender, **kwargs):
            ipn_obj = sender
            # You need to check 'payment_status' of the IPN

            if ipn_obj.payment_status == "Completed":
                # Undertake some action depending upon `ipn_obj`.
                if ipn_obj.custom == "Upgrade all users!":
                    Users.objects.update(paid=True)
            else
                ...

        payment_was_successful.connect(show_me_the_money)

   The data variables that are return on the IPN object are documented here:

   https://developer.paypal.com/webapps/developer/docs/classic/ipn/integration-guide/IPNandPDTVariables/

   You need to pay particular attention to `payment_status`.

1. You will also need to implement the 'return_url' and 'cancel_return' views
   to handle someone returning from PayPal. Note that these views need
   @csrf_exempt applied to them, because PayPal will POST to them, so they
   should be custom views that don't need to handle POSTs otherwise.

   For 'return_url' you need to cope with the possibility that the IPN has not
   yet been received and handled by the IPN listener you implemented (which can
   happen rarely), or that there was some kind of error with the IPN.


Using PayPal Payments Standard PDT:
-----------------------------------

Paypal Payment Data Transfer (PDT) allows you to display transaction details to
a customer immediately on return to your site unlike PayPal IPN which may take
some seconds. [You will need to enable PDT in your PayPal account to use it](https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/howto_html_paymentdatatransfer).

1. Download the code from GitHub:

        git clone git://github.com/spookylukey/django-paypal.git paypal

1. Edit `settings.py` and add  `paypal.standard.pdt` to your `INSTALLED_APPS`. Also set `PAYPAL_IDENTITY_TOKEN` - you can find the correct value of this setting from the PayPal website:

        # settings.py
        ...
        INSTALLED_APPS = (... 'paypal.standard.pdt', ...)

        PAYPAL_IDENTITY_TOKEN = "xxx"

        # For installations on which you want to use the sandbox,
        # set PAYPAL_TEST to True:
        # PAYPAL_TEST = True

1. Create a view that uses `PayPalPaymentsForm` just like in PayPal IPN.

1. After someone uses this button to buy something PayPal will return the user to your site at
   your "return_url" with some extra GET parameters. PayPal calls this Payment Data Transfer (PDT).
   The view `paypal.standard.pdt.views.pdt` handles PDT processing. to specify the correct
    `return_url` add the following to your `urls.py`:

       # urls.py
       ...
       urlpatterns = patterns('',
           (r'^paypal/pdt/', include('paypal.standard.pdt.urls')),
           ...
       )

Using PayPal Payments Standard with Subscriptions:
--------------------------------------------------

1. For subscription actions, you'll need to add a parameter to tell it to use
   the subscription buttons and the command, plus any subscription-specific
   settings:

        # views.py
        ...
        paypal_dict = {
           "cmd": "_xclick-subscriptions",
           "business": "your_account@paypal",
           "a3": "9.99",                      # monthly price
           "p3": 1,                           # duration of each unit (depends on unit)
           "t3": "M",                         # duration unit ("M for Month")
           "src": "1",                        # make payments recur
           "sra": "1",                        # reattempt payment on payment error
           "no_note": "1",                    # remove extra notes (optional)
           "item_name": "my cool subscription",
           "notify_url": "http://www.example.com/your-ipn-location/",
           "return_url": "http://www.example.com/your-return-location/",
           "cancel_return": "http://www.example.com/your-cancel-location/",
       }

       # Create the instance.
       form = PayPalPaymentsForm(initial=paypal_dict, button_type="subscribe")

        # Output the button.
        form.render()
        ...

Using PayPal Payments Standard with Encrypted Buttons:
------------------------------------------------------

Use this method to encrypt your button so sneaky gits don't try to hack
it. Thanks to [Jon Atkinson](http://jonatkinson.co.uk/) for the
[tutorial](http://jonatkinson.co.uk/paypal-encrypted-buttons-django/).

1. Encrypted buttons require the `M2Crypto` library:

        easy_install M2Crypto

1. Encrypted buttons require certificates. Create a private key:

        openssl genrsa -out paypal.pem 1024

1. Create a public key:

        openssl req -new -key paypal.pem -x509 -days 365 -out pubpaypal.pem

1. Upload your public key to the paypal website (sandbox or live).

    [https://www.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert](https://www.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert)

    [https://www.sandbox.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert](https://www.sandbox.paypal.com/us/cgi-bin/webscr?cmd=_profile-website-cert)

1. Copy your `cert id` - you'll need it in two steps. It's on the screen where
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

1. Verify that your IPN endpoint is running on SSL - `request.is_secure()` should return `True`!


Using PayPal Payments Pro (WPP)
-------------------------------

PayPal Payments Pro (or "Website Payments Pro") is a more awesome version of
PayPal that lets you accept payments on your site. This is now documented by
PayPal as a [Classic
API](https://developer.paypal.com/webapps/developer/docs/classic/products/) and
should not be confused with the "PayPal Payments Pro (Payflow Edition)" which is
a newer API.

The PayPal Payments Pro solution reuses code from `paypal.standard` so you'll
need to include both apps. django-paypal makes the whole process incredibly easy
to use through the provided `PayPalPro` class.

1. Obtain PayPal Pro API credentials: login to PayPal, click *My Account*,
  *Profile*, *Request API credentials*, *Set up PayPal API credentials and
  permissions*, *View API Signature*.

2. Edit `settings.py` and add  `paypal.standard` and `paypal.pro` to your
   `INSTALLED_APPS` and put in your PayPal Pro API credentials.

        # settings.py
        ...
        INSTALLED_APPS = (... 'paypal.standard', 'paypal.pro', ...)
        PAYPAL_TEST = True
        PAYPAL_WPP_USER = "???"
        PAYPAL_WPP_PASSWORD = "???"
        PAYPAL_WPP_SIGNATURE = "???"

3. Run `python manage.py syncdb` to add the required tables.

4. Write a wrapper view for `paypal.pro.views.PayPalPro`:

        # views.py
        from paypal.pro.views import PayPalPro

        def buy_my_item(request):
          item = {"amt": "10.00",             # amount to charge for item
                  "inv": "inventory",         # unique tracking variable paypal
                  "custom": "tracking",       # custom tracking variable for you
                  "cancelurl": "http://...",  # Express checkout cancel url
                  "returnurl": "http://..."}  # Express checkout return url

          kw = {"item": item,                            # what you're selling
                "payment_template": "payment.html",      # template name for payment
                "confirm_template": "confirmation.html", # template name for confirmation
                "success_url": "/success/"}              # redirect location after success

          ppp = PayPalPro(**kw)
          return ppp(request)


5. Create templates for payment and confirmation. By default both templates are
   populated with the context variable `form` which contains either a
   `PaymentForm` or a `Confirmation` form.

        <!-- payment.html -->
        <h1>Show me the money</h1>
        <form method="post" action="">
          {{ form }}
          <input type="submit" value="Pay Up">
        </form>

        <!-- confirmation.html -->
        <h1>Are you sure you want to buy this thing?</h1>
        <form method="post" action="">
          {{ form }}
          <input type="submit" value="Yes I Yams">
        </form>

6. Add your view to `urls.py`, and add the IPN endpoint to receive callbacks
   from PayPal:

        # urls.py
        ...
        urlpatterns = ('',
            ...
            (r'^payment-url/$', 'myproject.views.buy_my_item')
            (r'^some/obscure/name/', include('paypal.standard.ipn.urls')),
        )

7. Connect to the provided signals and have them do something useful:
    - `payment_was_successful`
    - `payment_was_flagged`


8. Profit.

Alternatively, if you want to get down to the nitty gritty and perform some
more advanced operations with Payments Pro, the `paypal.pro.helpers.PayPalWPP`
class provides the following methods:

* createBillingAgreement
    
    The CreateBillingAgreement API operation creates a billing agreement with
    a PayPal account holder. CreateBillingAgreement is only valid for
    reference transactions.
```python
from paypal.pro.helpers import PayPalWPP
        
def create_billing_agreement_view(request):
    wpp = PayPalWPP(request)
    token = request.GET.get('token')
    wpp.createBillingAgreement({'token': token})
    ...
```

* createRecurringPaymentsProfile

    The CreateRecurringPaymentsProfile API operation creates a recurring
    payments profile. You must invoke the CreateRecurringPaymentsProfile API
    operation for each profile you want to create. The API operation creates
    a profile and an associated billing agreement.
    
    **Note:** There is a one-to-one correspondence between billing agreements
    and recurring payments profiles. To associate a recurring payments
    profile with its billing agreement, you must ensure that the description
    in the recurring payments profile matches the description of a billing
    agreement. For version 54.0 and later, use SetExpressCheckout to initiate
    creation of a billing agreement.

* doDirectPayment

    The DoDirectPayment API Operation enables you to process a credit card
    payment.

* doExpressCheckoutPayment

    The DoExpressCheckoutPayment API operation completes an Express Checkout
    transaction. If you set up a billing agreement in your SetExpressCheckout
    API call, the billing agreement is created when you call the
    DoExpressCheckoutPayment API operation.
    
    The `DoExpressCheckoutPayment` API operation completes an Express
    Checkout transaction. If you set up a billing agreement in your
    `SetExpressCheckout` API call, the billing agreement is created when you
    call the `DoExpressCheckoutPayment` API operation.

* doReferenceTransaction

    The DoReferenceTransaction API operation processes a payment from a buyer's
    account, which is identified by a previous transaction.
```python
from paypal.pro.helpers import PayPalWPP

def do_reference_transaction_view(request):
    wpp = PayPalWPP(request)
    reference_id = request.POST.get('reference_id')
    amount = request.POST.get('amount')
    wpp.doReferenceTransaction({'referenceid': reference_id, 'amt': amount})
    ...
```

* getExpressCheckoutDetails

    The GetExpressCheckoutDetails API operation obtains information about a
    specific Express Checkout transaction.

* getTransactionDetails

    The GetTransactionDetails API operation obtains information about a
    specific transaction.

* manageRecurringPaymentsProfileStatus

    The ManageRecurringPaymentsProfileStatus API operation cancels, suspends,
    or reactivates a recurring payments profile.

* setExpressCheckout

    The SetExpressCheckout API operation initiates an Express Checkout
    transaction.

* updateRecurringPaymentsProfile

    The UpdateRecurringPaymentsProfile API operation updates a recurring
    payments profile.


Links:
------

[Set your IPN Endpoint on the PayPal Sandbox](https://www.sandbox.paypal.com/us/cgi-bin/webscr?cmd=_profile-ipn-notify)

[Django PayPal on Google Groups](http://groups.google.com/group/django-paypal)

[paypalhtml]: https://developer.paypal.com/webapps/developer/docs/classic/paypal-payments-standard/integration-guide/Appx_websitestandard_htmlvariables/ "PayPal HTML variables documentation"
