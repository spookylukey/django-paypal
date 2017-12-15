Using PayPal Standard with Subscriptions
========================================

For subscription actions, you'll need to add a parameter to tell it to use the
subscription buttons and the command, plus any subscription-specific settings:

views.py:

.. code-block:: python

    paypal_dict = {
       "cmd": "_xclick-subscriptions",
       "business": 'receiver_email@example.com',
       "a3": "9.99",                      # monthly price
       "p3": 1,                           # duration of each unit (depends on unit)
       "t3": "M",                         # duration unit ("M for Month")
       "src": "1",                        # make payments recur
       "sra": "1",                        # reattempt payment on payment error
       "no_note": "1",                    # remove extra notes (optional)
       "item_name": "my cool subscription",
       "notify_url": "http://www.example.com/your-ipn-location/",
       "return": "http://www.example.com/your-return-location/",
       "cancel_return": "http://www.example.com/your-cancel-location/",
   }

   # Create the instance.
   form = PayPalPaymentsForm(initial=paypal_dict, button_type="subscribe")

   # Output the button.
   form.render()


See `PayPal Subscribe button docs
<https://developer.paypal.com/docs/classic/paypal-payments-standard/integration-guide/subscribe_buttons/>`_.
