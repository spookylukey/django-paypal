
IPN/PDT variables
=================

The data variables that are returned on the IPN object are documented here:

https://developer.paypal.com/docs/api-basics/notifications/ipn/IPNandPDTVariables/

.. note:: The names of these data variables are not the same as the values that
          you `pass to PayPal
          <https://developer.paypal.com/webapps/developer/docs/classic/paypal-payments-standard/integration-guide/Appx_websitestandard_htmlvariables/>`_ -
          ensure you are looking at the right list!


The IPN/PDT objects are Django models with the same attributes as above,
converted to appropriate Python types e.g. ``Decimal`` for money values.

Where a variable has multiple values represented with *x* in the above
documentation, the corresponding fields do not exist on the model objects.
However, you can still access the data using the ``posted_data_dict`` attribute,
which returns a dictionary of all data sent by PayPal.

When processing these objects for handling payments, you need to pay particular
attention to ``payment_status`` (`docs
<https://developer.paypal.com/docs/api-basics/notifications/ipn/IPNandPDTVariables/#payment-information-variables>`_).
You can use the ``ST_PP_*`` constants in ``paypal.standard.models`` to help.
