Website Payments Pro models and helpers
=======================================


.. py:currentmodule:: paypal.pro.helpers

.. py:class:: PayPalWPP

   This class wraps the PayPal classic APIs, and sends data using Name-Value
   Pairs (NVP). The methods all take a ``params`` dictionary, the contents of
   which depend on the API being called. All parameter keys should be passed as
   lowercase values (unless otherwise specified), not the mixed case/upper case
   that is shown in PayPal docs.

   For API parameters, see the PayPal docs for more information:

   * `Express Checkout APIs <https://developer.paypal.com/docs/classic/api/>`_

   The method calls all return a :class:`paypal.pro.models.PayPalNVP` object on
   success. If an API call does not return ``ack=Success`` or
   ``ack=SuccessWithWarning``, a ``PayPalFailure`` exception is raised. The NVP
   object is available as an attribute named ``nvp`` on this exception object.


   .. py:method:: __init__(request=None, params=BASE_PARAMS)

      Initialize the instance using an optional Django HTTP request object, and
      an optional parameter dictionary which should contain the keys ``USER``,
      ``PWD``, ``SIGNATURE`` and ``VERSION``. If the parameter dictionary is not
      supplied, these parameters will be taken from settings
      ``PAYPAL_WPP_USER``, ``PAYPAL_WPP_PASSWORD``, ``PAYPAL_WPP_SIGNATURE`` and
      the builtin version number.

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
      transaction. Returns an ``PayPalNVP`` object that has the token saved
      in the ``.token`` attribute.

      This token can be converted into a URL to redirect to using the helper
      function ``express_endpoint_for_token`` in this module.

      See the `SetExpressCheckout docs
      <https://developer.paypal.com/docs/classic/api/merchant/SetExpressCheckout_API_Operation_NVP/>`_

   .. py:method:: updateRecurringPaymentsProfile()

      The UpdateRecurringPaymentsProfile API operation updates a recurring
      payments profile.

.. py:function:: express_endpoint_for_token(token, commit=False)

    Returns the PayPal Express Checkout endpoint for a token. Pass
    ``commit=True`` if you will not prompt for confirmation when the user
    returns to your site.

.. py:currentmodule:: paypal.pro.models

.. py:class:: PayPalNVP

   This stores the response returned by PayPal for any of the API calls above.

   It has fields for all the common values. For other values, you can access
   ``response_dict`` which is a dictionary-like object containing everything
   PayPal returned.
