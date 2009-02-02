#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings


class PayPalIPN(models.Model):
    """
    Logs PayPal IPN interactions.
    
    """    
    # 20:18:05 Jan 30, 2009 PST - PST timezone support is not included out of the box.
    PAYPAL_DATE_FORMAT = ("%H:%M:%S %b. %d, %Y PST", "%H:%M:%S %b %d, %Y PST",)
    
    # ### Todo: Choices fields? in or out?
    # FLAG_CODE_CHOICES = (
    # PAYMENT_STATUS_CHOICES = (Canceled_ Reversal Completed Denied Expired
    #    Failed Pending Processed Refunded Reversed Voided
    # AUTH_STATUS_CHOICES = (Completed Pending Voided)
    # ADDRESS_STATUS_CHOICES = (confirmed / unconfirmed)
    # PAYER_STATUS_CHOICES = (verified / unverified)
    # PAYMENT_TYPE_CHOICES =  echeck / instant
    # PENDING_REASON = address authorization echeck intl multi-currency unilateral upgrade verify other
    # REASON_CODE = chargeback guarantee buyer_complaint refund other
    # TRANSACTION_ENTITY_CHOICES = auth reauth order payment
    
    # Buyer information.
    address_city = models.CharField(max_length=40, blank=True)
    address_country = models.CharField(max_length=64, blank=True)
    address_country_code = models.CharField(max_length=64, blank=True, help_text="ISO 3166")
    address_name = models.CharField(max_length=128, blank=True)
    address_state = models.CharField(max_length=40, blank=True)
    address_status = models.CharField(max_length=11, blank=True)
    address_street = models.CharField(max_length=200, blank=True)
    address_zip = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    payer_business_name = models.CharField(max_length=127, blank=True)
    payer_email = models.CharField(max_length=127, blank=True)
    payer_status= models.CharField(max_length=32, blank=True)
    payer_id = models.CharField(max_length=13, blank=True)
    payer_status = models.CharField(max_length=10, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    residence_country = models.CharField(max_length=2, blank=True)

    # Basic information.
    business = models.CharField(max_length=127, blank=True, help_text="Email where the money was sent.")
    item_name = models.CharField(max_length=127, blank=True)
    item_number = models.CharField(max_length=127, blank=True)
    quantity = models.IntegerField(blank=True, default=1, null=True)
    receiver_email = models.EmailField(max_length=127, blank=True)
    receiver_id = models.CharField(max_length=127, blank=True)  # 258DLEHY2BDK6

    # Merchant specific.
    custom = models.CharField(max_length=255, blank=True)
    invoice = models.CharField(max_length=127, blank=True)
    memo = models.CharField(max_length=255, blank=True)
    
    # Website payments standard.
    auth_id = models.CharField(max_length=19, blank=True)
    auth_exp = models.CharField(max_length=28, blank=True)
    auth_amount = models.FloatField(default=0, blank=True, null=True)
    auth_status = models.CharField(max_length=9, blank=True) 
    mc_gross = models.FloatField(default=0, blank=True, null=True)
    mc_fee = models.FloatField(default=0, blank=True, null=True)
    mc_currency = models.CharField(max_length=32, default="USD", blank=True)
    currency_code = models.CharField(max_length=32, default="USD", blank=True)
    payment_cycle= models.CharField(max_length=32, blank=True) #Monthly
    payment_fee = models.FloatField(default=0, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True, help_text="HH:MM:SS DD Mmm YY, YYYY PST")
    next_payment_date = models.DateTimeField(blank=True, null=True, help_text="HH:MM:SS DD Mmm YY, YYYY PST")
    payment_status = models.CharField(max_length=9, blank=True)
    payment_type = models.CharField(max_length=7, blank=True)
    pending_reason = models.CharField(max_length=14, blank=True)
    reason_code = models.CharField(max_length=15, blank=True)
    transaction_entity = models.CharField(max_length=7, blank=True)
    txn_id = models.CharField("Transaction ID", max_length=19, blank=True, help_text="PayPal transaction ID.")
    txn_type= models.CharField("Transaction Type", max_length=32, blank=True, help_text="PayPal transaction type.")
    parent_txn_id = models.CharField("Parent Transaction ID", max_length=19, blank=True)

    # Additional information - full IPN query and time fields.
    test_ipn = models.BooleanField(default=False, blank=True)
    ip = models.IPAddressField(blank=True)
    flag = models.BooleanField(default=False, blank=True)
    flag_code = models.CharField(max_length=16, blank=True)
    flag_info = models.TextField(blank=True)
    query = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Recurring Payments:
    profile_status = models.CharField(max_length=32, blank=True) 
    initial_payment_amount = models.FloatField(default=0, blank=True, null=True)
    amount_per_cycle = models.FloatField(default=0, blank=True, null=True)
    outstanding_balance = models.FloatField(default=0, blank=True, null=True)
    period_type = models.CharField(max_length=32, blank=True)
    product_name = models.CharField(max_length=128, blank=True)
    product_type= models.CharField(max_length=128, blank=True)
    recurring_payment_id = models.CharField(max_length=128, blank=True)  # I-FA4XVST722B9
    receipt_id= models.CharField(max_length=64, blank=True)  # 1335-7816-2936-1451

    # ### To-do: Unimplemnted fields that you mightw want to think about.
    # mc_handling
    # mc_shipping
    # num_cart_items
    # option_name1
    # option_name2
    # option_selection1_x
    # option_selection2_x
    # shipping_method
    # shipping
    # tax

    class Meta:
        db_table = "paypal_ipn"

    def __unicode__(self):
        return "<PayPalIPN: %s>" % self.txn_id
        
    def _postback(self):
        """
        Perform PayPal Postback validation.
        Sends the received data back to PayPal which responds with verified or invalid.
        Flags the payment if the response is invalid.
        Returns True if the postback is verified.
        
        """
        import urllib2
        
        # ### Todo: Add code to choose sandbox or live.
        # ENDPOINT = "https://www.paypal.com/cgi-bin/webscr"
        ENDPOINT = "https://www.sandbox.paypal.com/cgi-bin/webscr"
        response = urllib2.urlopen(ENDPOINT, "cmd=_notify-validate&%s" % self.query).read()
        if response == "VERIFIED":
            return False
        else:
            self.set_flag("Invalid postback.")
            return True
                    
    def verify(self, item_check_callable=None):
        """
        Verifies an IPN.
        Checks for obvious signs of weirdness in the payment and flags appropriately.
        
        You can provide a function `item_check_callabe` that takes a PayPalIPN instance
        and returns (True, None) if the item is valid. Returns (False, "reason") if
        the item isn't valid. This function should check that `mc_gross`, `mc_currency`
        `item_name` and `item_number` are all correct.

        """
        from paypal.standard.helpers import duplicate_txn_id
        
        if self._postback():
            if self.payment_status != "Completed":
                self.set_flag("Invalid payment_status.")
            if duplicate_txn_id(self):
                self.set_flag("Duplicate transaction ID.")
            if self.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
                self.set_flag("Invalid receiver_email.")
            if callable(item_check_callable):
                flag, reason = item_check_callable(self)
                if flag:
                    self.set_flag(reason)
                
    def verify_secret(self, form_instance, secret):
        """
        Verifies an IPN payment over SSL using EWP. 
        
        """
        from paypal.standard.helpers import check_secret
        if not check_secret(form_instance, secret):
            self.set_flag("Invalid secret.")

    def set_flag(self, info, code=None):
        """
        Sets a flag on the transaction and also sets a reason.
        
        """
        self.flag = True
        self.flag_info += info
        if code is not None:
            self.flag_code = code
    

class PayPalIPNExtended(PayPalIPN):
    """
    Idea for extending the PayPalIPN class to include other tasty IPN variables.

    """
    # Advanced and custom information.
    # option_name_1
    # option_name_2
    # option_selection1
    # option_selection2
    # tax
    
    # Refund info.
    
    # Currency and currency exchange.
    
    # Auctions.
    
    # Mass payment.
    
    # Subscription variables.
    
    # Dispute notifications.
    
    class Meta:
        abstract = True