#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.forms.models import model_to_dict

from paypal.pro.fields import CountryField
from paypal.pro.helpers import PayPalWPP
from paypal.pro.signals import payment_was_successful, payment_was_flagged


class BasePaymentInfo(models.Model):
    """
    Base model suitable for representing a payment!    

    """
    firstname = models.CharField("First Name", max_length=255)
    lastname = models.CharField("Last Name", max_length=255)
    street = models.CharField("Street Address", max_length=255)
    city = models.CharField("City", max_length=255)
    state = models.CharField("State", max_length=255)
    countrycode = CountryField("Country", default="US")
    zip = models.CharField("Zipcode", max_length=32)

    # ### Todo: add hidden item name and invoice blah blah blah fields.ow you'

    class Meta:
        abstract = True
        
class PaymentInfo(BasePaymentInfo):
    """
    Payment model with a bit more information.

    """    
    user = models.ForeignKey('auth.user', null=True)
    # Admin fields:    
    ipaddress = models.IPAddressField(blank=True)
    flag = models.BooleanField(default=False, blank=True)
    flag_code = models.CharField(max_length=16, blank=True)
    flag_info = models.TextField(blank=True)
    query = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
    def init(self, request):
        self.ipaddress = request.META.get('REMOTE_ADDR', '')
        self.query = request.POST.urlencode()
        if request.user.is_authenticated():
            self.user = request.user

    def set_flag(self, info, code=None):
        self.flag = True
        self.flag_info += info
        if code is not None:
            self.flag_code = code


class PayPalPaymentInfo(PaymentInfo):
    """
    Payment model with paypal attack methods.
    
    """
    ADMIN_FIELDS = "id user ipaddress flag flag_code flag_info query created_at updated_at response".split()
    ITEM_FIELDS = "amt custom invnum".split()
    
    amt = models.FloatField()
    custom = models.CharField(max_length=255, blank=True)
    invnum = models.CharField(max_length=127, blank=True)
    response = models.TextField(blank=True)
    
    class Meta:
        db_table = "paypal_paymentinfo"
        
    def process(self, request, item_data):
        """
        Do a direct payment.
        
        """
        # Change the model information into a dict that PayPal can understand.        
        params = model_to_dict(self, exclude=self.ADMIN_FIELDS)
        # Grab the non-model params we stashed in the form.save
        params['ipaddress'] = self.ipaddress
        params['acct'] = self.acct
        params['creditcardtype'] = self.creditcardtype
        params['expdate'] = self.expdate
        params['cvv2'] = self.cvv2
        params.extend(item_data)      
        
        # Make the request to PayPal - this could take some time.
        wpp = PayPalWPP()
        response = wpp.doDirectPayment(params)
        
        # Store the response.
        self.response = repr(response)
        
        if response['ACK'] != "Success":
            self.set_flag(response.get('L_LONGMESSAGE0', ''), response.get('L_ERRORCODE0', ''))
            payment_was_flagged.send(sender=self, response=response, request=request)
            return False
        else:
            payment_was_successful.send(sender=self, response=response, request=request)
            return True
        
        # Example success:
        # {'ACK': 'Success', 'TIMESTAMP': '2009-02-02T04:11:35Z', 'CURRENCYCODE': 'USD', 'VERSION': '50.0', 'BUILD': '758866', 'TRANSACTIONID': '9FM85230E94631618', 'AVSCODE': 'X', 'AMT': '10.00', 'CORRELATIONID': 'c7f3e88d983e', 'CVV2MATCH': 'M'}

        # Example fail:
        # {'ACK': 'Failure', 'TIMESTAMP': '2009-02-02T04:13:52Z', 'CURRENCYCODE': 'USD', 'L_SEVERITYCODE0': 'Error', 'L_SHORTMESSAGE0': 'Invalid Data', 'L_LONGMESSAGE0': 'The transaction was refused as a result of a duplicate invoice ID supplied.  Attempt with a new invoice ID', 'VERSION': '50.0', 'BUILD': '758866', 'L_ERRORCODE0': '10536', 'AMT': '10.00', 'CORRELATIONID': '5aa73301923fc'}



# class PayPalResponse(models.Model):
# 
#     amount
#     avs
#     cvv
#     tnx_id
#     error_cdoes
#     corrlection_id
    
#         
# 
# class PayPalPro(models.model)
# 
# """
# If the operation is successful, you should send your customer to an order confirmation 
# page. 
# The Ack code determines whether the operation is a success. If successful, you should 
# display a message on the order confirmation page. 
# If not successful, which is either a failure or a success with warning due to Fraud 
# Management Filters, you should display information related to the error. In addition, you 
# may want to provide your customer an opportunity to pay using a different payment 
# method. 
# 
# 
# """
# 
# 
# – Ack code (Success, SuccessWithWarning, or Failure) 
# – Amount of the transaction 
# – AVS response code 
# – CVV response code 
# – PayPal transaction ID 
# – Error codes and messages (if any) 
# – Correlation ID (unique identifier for the API call) 
# 
# Your checkout pages must collect all the information you need to create the 
# DoDirectPayment request. The following recommendations make it easier for your 
# customers to provide the needed information and aid in the correct processing of the request: 
# Provide a drop-down menu for the “state” or “province” fields. For US addresses, the state 
# must be two letters, and must be a valid two-letter state, military location, or US territory. 
# For Canada, the province must be a two-letter Canadian province. 
# Ensure customers can enter the correct number of digits for the CVV code. The value is 3 
# digits for Visa, MasterCard, and Discover. The value is 4 digits for American Express. 
# Show information on the checkout page that explains what CVV is, and where to find it on 
# the card.
# 
# Configure timeout settings to allow for the fact that the DoDirectPayment API operation 
# can take up to 30 seconds. Consider displaying a “processing transaction” message to your 
# customer and disabling the Pay button until the transaction finishes. 
# Use the optional Invoice ID field to prevent duplicate charges. PayPal ensures that an 
# Invoice ID is used only once per account. Duplicate requests with the same Invoice ID 
# result in an error and a failed transaction.