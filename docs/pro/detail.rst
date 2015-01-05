Website Payments Pro detail
===========================

.. py:currentmodule:: paypal.pro.helpers

.. py:class:: PayPalWPP

   .. py:method:: createBillingAgreement()

      The CreateBillingAgreement API operation creates a billing agreement with
      a PayPal account holder. CreateBillingAgreement is only valid for
      reference transactions.

      .. code-block:: python

          from paypal.pro.helpers import PayPalWPP

          def create_billing_agreement_view(request):
              wpp = PayPalWPP(request)
              token = request.GET.get('token')
              wpp.createBillingAgreement({'token': token})

   .. py:method:: createRecurringPaymentsProfile()

      The CreateRecurringPaymentsProfile API operation creates a recurring
      payments profile. You must invoke the CreateRecurringPaymentsProfile API
      operation for each profile you want to create. The API operation creates a
      profile and an associated billing agreement.

      **Note:** There is a one-to-one correspondence between billing agreements
      and recurring payments profiles. To associate a recurring payments profile
      with its billing agreement, you must ensure that the description in the
      recurring payments profile matches the description of a billing
      agreement. For version 54.0 and later, use SetExpressCheckout to initiate
      creation of a billing agreement.


   .. py:method:: doDirectPayment()

      The DoDirectPayment API Operation enables you to process a credit card
      payment.

   .. py:method:: doExpressCheckoutPayment()

      The DoExpressCheckoutPayment API operation completes an Express Checkout
      transaction. If you set up a billing agreement in your SetExpressCheckout
      API call, the billing agreement is created when you call the
      DoExpressCheckoutPayment API operation.

      The `DoExpressCheckoutPayment` API operation completes an Express Checkout
      transaction. If you set up a billing agreement in your
      `SetExpressCheckout` API call, the billing agreement is created when you
      call the `DoExpressCheckoutPayment` API operation.

   .. py:method:: doReferenceTransaction()

      The DoReferenceTransaction API operation processes a payment from a
      buyer's account, which is identified by a previous transaction.

      .. code-block:: python

         from paypal.pro.helpers import PayPalWPP

         def do_reference_transaction_view(request):
             wpp = PayPalWPP(request)
             reference_id = request.POST.get('reference_id')
             amount = request.POST.get('amount')
             wpp.doReferenceTransaction({'referenceid': reference_id, 'amt': amount})

   .. py:method:: getExpressCheckoutDetails()

      The GetExpressCheckoutDetails API operation obtains information about a
      specific Express Checkout transaction.

   .. py:method:: getTransactionDetails()

      The GetTransactionDetails API operation obtains information about a
      specific transaction.

   .. py:method:: manageRecurringPaymentsProfileStatus()

      The ManageRecurringPaymentsProfileStatus API operation cancels, suspends,
      or reactivates a recurring payments profile.

   .. py:method:: setExpressCheckout()

      The SetExpressCheckout API operation initiates an Express Checkout
      transaction.

   .. py:method:: updateRecurringPaymentsProfile()

      The UpdateRecurringPaymentsProfile API operation updates a recurring
      payments profile.
