#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings

# ### ToDo: would be cool if PayPalIPN.query was a JSON field
# ### or something else that let you get at the data better.

# ### ToDo: Should the signal be in `set_flag` or `verify`?
# ### ToDo: There are a # of fields that appear to be duplicates from PayPal
# ### can we sort them out?

# ### Todo: PayPalIPN choices fields? in or out?

# ### Todo: Does anyone really want all these fields or just a subset?

POSTBACK_ENDPOINT = "https://www.paypal.com/cgi-bin/webscr"
SANDBOX_POSTBACK_ENDPOINT = "https://www.sandbox.paypal.com/cgi-bin/webscr"

class PayPalStandardBase(models.Model):
    """
    Common variables shared by IPN and PDT
    https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_html_IPNandPDTVariables
    """
    # FLAG_CODE_CHOICES = (
    # PAYMENT_STATUS_CHOICES = "Canceled_ Reversal Completed Denied Expired Failed Pending Processed Refunded Reversed Voided".split()
    # AUTH_STATUS_CHOICES = "Completed Pending Voided".split()
    # ADDRESS_STATUS_CHOICES = "confirmed unconfirmed".split()
    # PAYER_STATUS_CHOICES = "verified / unverified".split()
    # PAYMENT_TYPE_CHOICES =  "echeck / instant.split()
    # PENDING_REASON = "address authorization echeck intl multi-currency unilateral upgrade verify other".split()
    # REASON_CODE = "chargeback guarantee buyer_complaint refund other".split()
    # TRANSACTION_ENTITY_CHOICES = "auth reauth order payment".split()
    
    # Transaction and Notification-Related Variables
    business = models.CharField(max_length=127, blank=True, help_text="Email where the money was sent.")
    charset=models.CharField(max_length=32, blank=True)
    custom = models.CharField(max_length=255, blank=True)
    notify_version = models.FloatField(default=0, blank=True, null=True)
    parent_txn_id = models.CharField("Parent Transaction ID", max_length=19, blank=True)
    receiver_email = models.EmailField(max_length=127, blank=True)
    receiver_id = models.CharField(max_length=127, blank=True)  # 258DLEHY2BDK6
    residence_country = models.CharField(max_length=2, blank=True)
    test_ipn = models.BooleanField(default=False, blank=True)
    txn_id = models.CharField("Transaction ID", max_length=19, blank=True, help_text="PayPal transaction ID.")
    txn_type = models.CharField("Transaction Type", max_length=128, blank=True, help_text="PayPal transaction type.")
    verify_sign = models.CharField(max_length=255, blank=True)    
    
    # Buyer Information Variables
    address_country = models.CharField(max_length=64, blank=True)
    address_city = models.CharField(max_length=40, blank=True)
    address_country_code = models.CharField(max_length=64, blank=True, help_text="ISO 3166")
    address_name = models.CharField(max_length=128, blank=True)
    address_state = models.CharField(max_length=40, blank=True)
    address_status = models.CharField(max_length=11, blank=True)
    address_street = models.CharField(max_length=200, blank=True)
    address_zip = models.CharField(max_length=20, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    payer_business_name = models.CharField(max_length=127, blank=True)
    payer_email = models.CharField(max_length=127, blank=True)
    payer_id = models.CharField(max_length=13, blank=True)
    
    # Payment Information Variables
    auth_amount = models.FloatField(default=0, blank=True, null=True)
    auth_exp = models.CharField(max_length=28, blank=True)
    auth_id = models.CharField(max_length=19, blank=True)
    auth_status = models.CharField(max_length=9, blank=True) 
    exchange_rate = models.FloatField(default=0, blank=True, null=True)
    # TODO: see https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_html_IPNandPDTVariables
    # fraud_managment_pending_filters_x = models.CharField(max_length=255, blank=True) 
    invoice = models.CharField(max_length=127, blank=True)
    item_name = models.CharField(max_length=127, blank=True)
    item_number = models.CharField(max_length=127, blank=True)
    mc_currency = models.CharField(max_length=32, default="USD", blank=True)
    mc_fee = models.FloatField(default=0, blank=True, null=True)
    mc_gross = models.FloatField(default=0, blank=True, null=True)
    # TODO: x refers to an item number, needs a model with foreign key to this transaction
    # mc_gross_x = models.FloatField(default=0, blank=True, null=True) 
    mc_handling = models.FloatField(default=0, blank=True, null=True)
    mc_shipping = models.FloatField(default=0, blank=True, null=True)
    mc_shippingx = models.FloatField(default=0, blank=True, null=True)
    memo = models.CharField(max_length=255, blank=True)
    num_cart_items = models.IntegerField(blank=True, default=0, null=True)
    option_name1 = models.CharField(max_length=64, blank=True)
    option_name2 = models.CharField(max_length=64, blank=True)
    # TODO: x refers to an item number, needs a model with foreign key to this transaction
    # option_selection1_x = models.CharField(max_length=200, blank=True) 
    # TODO: x refers to an item number, needs a model with foreign key to this transaction
    # option_selection2_x = models.CharField(max_length=200, blank=True) 
    payer_status = models.CharField(max_length=10, blank=True)
    payment_date = models.DateTimeField(blank=True, null=True, help_text="HH:MM:SS DD Mmm YY, YYYY PST")
    # payment_fee = models.FloatField(default=0, blank=True, null=True) # DEPRECATED
    # payment_fee_x = models.FloatField(default=0, blank=True, null=True) # DEPRECATED
    payment_gross = models.FloatField(default=0, blank=True, null=True)
    # payment_gross_x = models.FloatField(default=0, blank=True, null=True) # DEPRECATED
    payment_status = models.CharField(max_length=9, blank=True)
    payment_type = models.CharField(max_length=7, blank=True)
    pending_reason = models.CharField(max_length=14, blank=True)
    protection_eligibility=models.CharField(max_length=32, blank=True)
    quantity = models.IntegerField(blank=True, default=1, null=True)
    reason_code = models.CharField(max_length=15, blank=True)
    remaining_settle = models.FloatField(default=0, blank=True, null=True)
    settle_amount = models.FloatField(default=0, blank=True, null=True)
    settle_currency = models.CharField(max_length=32, blank=True)
    shipping = models.FloatField(default=0, blank=True, null=True)
    shipping_method = models.CharField(max_length=255, blank=True)
    tax = models.FloatField(default=0, blank=True, null=True)
    transaction_entity = models.CharField(max_length=7, blank=True)
    
    # Auction Variables
    auction_buyer_id = models.CharField(max_length=64, blank=True)
    auction_closing_date = models.DateTimeField(blank=True, null=True, help_text="HH:MM:SS DD Mmm YY, YYYY PST")
    auction_multi_item = models.IntegerField(blank=True, default=0, null=True)
    for_auction = models.FloatField(default=0, blank=True, null=True)
    
    
    # Mass Pay Variables (Not Implemented, needs a separate model, for each transaction x)
    """
    masspay_txn_id_x = models.CharField(max_length=19, blank=True)
    mc_currency_x = models.CharField(max_length=32, default="USD", blank=True)
    mc_fee_x = models.FloatField(default=0, blank=True, null=True)
    mc_gross_x = models.FloatField(default=0, blank=True, null=True)
    mc_handlingx = models.FloatField(default=0, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True, help_text="HH:MM:SS DD Mmm YY, YYYY PST")
    payment_status = models.CharField(max_length=9, blank=True)
    reason_code = models.CharField(max_length=15, blank=True)
    receiver_email_x = models.EmailField(max_length=127, blank=True)
    status_x = models.CharField(max_length=9, blank=True)
    unique_id_x = models.CharField(max_length=13, blank=True)
    """
        
    # Recurring Payments Variables
    amount = models.FloatField(default=0, blank=True, null=True)
    amount_per_cycle = models.FloatField(default=0, blank=True, null=True)
    initial_payment_amount = models.FloatField(default=0, blank=True, null=True)
    next_payment_date = models.DateTimeField(blank=True, null=True, help_text="HH:MM:SS DD Mmm YY, YYYY PST")
    outstanding_balance = models.FloatField(default=0, blank=True, null=True)
    payment_cycle= models.CharField(max_length=32, blank=True) #Monthly
    period_type = models.CharField(max_length=32, blank=True)
    product_name = models.CharField(max_length=128, blank=True)
    product_type= models.CharField(max_length=128, blank=True)    
    profile_status = models.CharField(max_length=32, blank=True)
    recurring_payment_id = models.CharField(max_length=128, blank=True)  # I-FA4XVST722B9
    rp_invoice_id= models.CharField(max_length=127, blank=True)  # 1335-7816-2936-1451
    time_created = models.DateTimeField(blank=True, null=True, help_text="HH:MM:SS DD Mmm YY, YYYY PST")
    
    # Subscription Variables
    amount1 = models.FloatField(default=0, blank=True, null=True)
    amount2 = models.FloatField(default=0, blank=True, null=True)
    amount3 = models.FloatField(default=0, blank=True, null=True)
    mc_amount1 = models.FloatField(default=0, blank=True, null=True)
    mc_amount2 = models.FloatField(default=0, blank=True, null=True)
    mc_amount3 = models.FloatField(default=0, blank=True, null=True)
    password = models.CharField(max_length=24, blank=True)
    period1 = models.CharField(max_length=32, blank=True)
    period2 = models.CharField(max_length=32, blank=True)
    period3 = models.CharField(max_length=32, blank=True)
    reattempt = models.CharField(max_length=1, blank=True)
    recur_times = models.IntegerField(blank=True, default=0, null=True)
    recurring = models.CharField(max_length=1, blank=True)
    retry_at = models.DateTimeField(blank=True, null=True, help_text="HH:MM:SS DD Mmm YY, YYYY PST")
    subscr_date = models.DateTimeField(blank=True, null=True, help_text="HH:MM:SS DD Mmm YY, YYYY PST")
    subscr_effective = models.DateTimeField(blank=True, null=True, help_text="HH:MM:SS DD Mmm YY, YYYY PST")
    subscr_id = models.CharField(max_length=19, blank=True)
    username = models.CharField(max_length=64, blank=True)
    
    # Dispute Resolution Variables
    case_creation_date = models.DateTimeField(blank=True, null=True, help_text="HH:MM:SS DD Mmm YY, YYYY PST")
    case_id = models.CharField(max_length=14, blank=True)
    case_type = models.CharField(max_length=24, blank=True)
    # reason_code = models.CharField(max_length=24, blank=True) # already have a reason_code above
    
    # Variables not categorized in paypal docs 
    # https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_html_IPNandPDTVariables
    receipt_id= models.CharField(max_length=64, blank=True)  # 1335-7816-2936-1451 
    currency_code = models.CharField(max_length=32, default="USD", blank=True)
    handling_amount = models.FloatField(default=0, blank=True, null=True)
    transaction_subject = models.CharField(max_length=255, blank=True)

    # Additional information - full IPN/PDT query and time fields.    
    ipaddress = models.IPAddressField(blank=True)
    flag = models.BooleanField(default=False, blank=True)
    flag_code = models.CharField(max_length=16, blank=True)
    flag_info = models.TextField(blank=True)
    query = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
    def is_transaction(self):
        return len(self.txn_id) > 0
    
    def is_recurring(self):
        return len(self.recurring_payment_id) > 0
    
    def set_flag(self, info, code=None):
        """Sets a flag on the transaction and also sets a reason."""
        self.flag = True
        self.flag_info += info
        if code is not None:
            self.flag_code = code
        
    def verify_secret(self, form_instance, secret):
        """Verifies an IPN payment over SSL using EWP. """
        from paypal.standard.helpers import check_secret
        if not check_secret(form_instance, secret):
            self.set_flag("Invalid secret.")

    def verify(self, item_check_callable=None, test=True):
        """
        Verifies an IPN and a PDT.
        Checks for obvious signs of weirdness in the payment and flags appropriately.
        
        Provide a callable that takes a PayPalIPN instances as a parameters and returns
        a tuple (True, Non) if the item is valid. Should return (False, "reason") if the
        item isn't valid. This function should check that `mc_gross`, `mc_currency`
        `item_name` and `item_number` are all correct.

        """
        from paypal.standard.helpers import duplicate_txn_id       
        html_content = self._postback(test)
        result = self._parse_paypal_response(html_content)  
        if result == True:
            if self.is_transaction():
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
            else:
                # ### To-Do: Need to run a different series of checks on recurring payments.
                pass
        else:
            self.set_flag("Postback failed.")
            
        self.save()      
        self.send_signals(result)
        
    def send_signals(self, result):
        """Define in concrete class."""
        pass
        
    def get_endpoint(self, test):
        if test:
            return SANDBOX_POSTBACK_ENDPOINT
        else:
            return POSTBACK_ENDPOINT    
    