Overview
========

Before diving in, a quick review of PayPal's payment methods is in order!
`PayPal Payments Standard
<https://developer.paypal.com/webapps/developer/docs/classic/paypal-payments-standard/integration-guide/wp_standard_overview/>`_
is the "Buy it Now" buttons you may have seen floating around the
internet. Buyers click on the button and are taken to PayPal's website where
they can pay for the product.

After this point, you can get notification of the payment using either Payment
Data Transfer (PDT) or Instant Payment Notification (IPN).

For IPN, as soon as PayPal has taken payment details, it sends a message to a
configured endpoint on your site in a separate HTTP request which you must
handle. It will make multiple attempts for the case of connectivity issues. This
method has the disadvantage that the user may arrive back at your site before
your site has been notified about the transaction.

For PDT, PayPal redirects the user back to your website with a transaction ID in
the query string. This has the disadvantage that if there is some kind of
connection issue at this point, you won't get notification. However, for the
success case, you can be sure that the information about the transaction arrives
at the same time as the users arrives back at your site.

PayPal Payments Pro allows you to accept payments on your website. It contains
two distinct payment flows: Direct Payment allows the user to enter credit card
information on your website and pay on your website. Express Checkout sends the
user over to PayPal to confirm their payment method before redirecting back to
your website for confirmation. PayPal rules state that both methods must be
implemented.

More recently, PayPal have implemented newer APIs, including "PayPal Payments
Pro (Payflow Edition)". This is not to be confused with the "Classic" PayPal
Payments Pro that is implemented by django-paypal. "Payflow Edition" is not yet
supported by django-paypal.


See also:

* :doc:`standard/index`
* :doc:`pro/index`
