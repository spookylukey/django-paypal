#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.http import urlencode
from django.http import QueryDict
import urllib2
from urllib import unquote_plus
from paypal.standard.signals import payment_was_successful, payment_was_flagged, pdt_failed, pdt_successful
import logging
from django.test.client import Client
from django.core.urlresolvers import reverse

# ### ToDo: would be cool if PayPalIPN.query was a JSON field
# ### or something else that let you get at the data better.

# ### ToDo: Should the signal be in `set_flag` or `verify`?
# ### ToDo: There are a # of fields that appear to be duplicates from PayPal
# ### can we sort them out?

# ### Todo: PayPalIPN choices fields? in or out?

POSTBACK_ENDPOINT = "https://www.paypal.com/cgi-bin/webscr"
SANDBOX_POSTBACK_ENDPOINT = "https://www.sandbox.paypal.com/cgi-bin/webscr"



class PayPalCommon(models.Model):
    """
    Common variables shared by IPN and PDT
    https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_html_IPNandPDTVariables
    """
    # 20:18:05 Jan 30, 2009 PST - PST timezone support is not included out of the box.
    # PAYPAL_DATE_FORMAT = ("%H:%M:%S %b. %d, %Y PST", "%H:%M:%S %b %d, %Y PST",)
    # PayPal dates have been spotted in the wild with these formats, beware!
    PAYPAL_DATE_FORMAT = ("%H:%M:%S %b. %d, %Y PST",
                          "%H:%M:%S %b. %d, %Y PDT",
                          "%H:%M:%S %b %d, %Y PST",
                          "%H:%M:%S %b %d, %Y PDT",)
    
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
    # fraud_managment_pending_filters_x = models.CharField(max_length=255, blank=True) # TODO: see https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_html_IPNandPDTVariables
    invoice = models.CharField(max_length=127, blank=True)
    item_name = models.CharField(max_length=127, blank=True)
    item_number = models.CharField(max_length=127, blank=True)
    mc_currency = models.CharField(max_length=32, default="USD", blank=True)
    mc_fee = models.FloatField(default=0, blank=True, null=True)
    mc_gross = models.FloatField(default=0, blank=True, null=True)
    # mc_gross_x = models.FloatField(default=0, blank=True, null=True) # TODO: x refers to an item number, needs a model with foreign key to this transaction
    mc_handling = models.FloatField(default=0, blank=True, null=True)
    mc_shipping = models.FloatField(default=0, blank=True, null=True)
    mc_shippingx = models.FloatField(default=0, blank=True, null=True)
    memo = models.CharField(max_length=255, blank=True)
    num_cart_items = models.IntegerField(blank=True, default=0, null=True)
    option_name1 = models.CharField(max_length=64, blank=True)
    option_name2 = models.CharField(max_length=64, blank=True)
    # option_selection1_x = models.CharField(max_length=200, blank=True) # TODO: x refers to an item number, needs a model with foreign key to this transaction
    # option_selection2_x = models.CharField(max_length=200, blank=True) # TODO: x refers to an item number, needs a model with foreign key to this transaction
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
        """
        Sets a flag on the transaction and also sets a reason.
        
        """
        self.flag = True
        self.flag_info += info
        if code is not None:
            self.flag_code = code
        
    def verify_secret(self, form_instance, secret):
        """
        Verifies an IPN payment over SSL using EWP. 
        
        """
        from paypal.standard.helpers import check_secret
        if not check_secret(form_instance, secret):
            self.set_flag("Invalid secret.")




class PayPalIPN(PayPalCommon):
    """
    Logs PayPal IPN interactions.    
    
    """

    class Meta:
        db_table = "paypal_ipn"
        verbose_name = "PayPal IPN"

    def __unicode__(self):
        fmt = u"<IPN: %s %s>"
        if self.is_transaction():
            return fmt % ("Transaction", self.txn_id)
        else:
            return fmt % ("Recurring", self.recurring_payment_id)
        
    
        
    def _postback(self, test=True):
        """
        Perform PayPal Postback validation.
        Sends the received data back to PayPal which responds with verified or invalid.
        Flags the payment if the response is invalid.
        Returns True if the postback is verified.
        
        """
        response = ""
        if hasattr(settings, 'PAYPAL_TESTING'):
            client = Client()
            paypal_http_response = client.get(reverse('paypal-fake-ipn-response'))
            response = paypal_http_response.content.strip()
        else:
            import urllib2
            if test:
                endpoint = SANDBOX_POSTBACK_ENDPOINT
            else:
                endpoint = POSTBACK_ENDPOINT
            response = urllib2.urlopen(endpoint, "cmd=_notify-validate&%s" % self.query).read()
        if response == "VERIFIED":
            return True
        else:
            self.set_flag("Invalid postback.")
            return False
                        
    def verify(self, item_check_callable=None, test=True):
        """
        Verifies an IPN.
        Checks for obvious signs of weirdness in the payment and flags appropriately.
        
        Provide a callable that takes a PayPalIPN instances as a parameters and returns
        a tuple (True, Non) if the item is valid. Should return (False, "reason") if the
        item isn't valid. This function should check that `mc_gross`, `mc_currency`
        `item_name` and `item_number` are all correct.

        """
        from paypal.standard.helpers import duplicate_txn_id        
        if self._postback(test):
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
            self.set_flag("FAIL")
            
        
        self.save()        
        if self.flag:
            payment_was_flagged.send(sender=self)
        else:
            payment_was_successful.send(sender=self)    

    def init(self, request):
        self.query = request.POST.urlencode()
        self.ipaddress = request.META.get('REMOTE_ADDR', '')
        
           
        
class PayPalPDT(PayPalCommon):
    
    amt = models.FloatField(default=0, blank=True, null=True)
    cm = models.CharField(max_length=255, blank=True)
    sig = models.CharField(max_length=255, blank=True)
    tx = models.CharField(max_length=255, blank=True)
    st = models.CharField(max_length=32, blank=True)
    
    class Meta:
        db_table = "paypal_pdt"
        verbose_name = "PayPal PDT"
    
    
    def init(self, request):
        self.query = request.GET.urlencode()
        self.ipaddress = request.META.get('REMOTE_ADDR', '')

    def _postback(self, test=True):
        """
        Perform PayPal PDT Postback validation.
        Sends the transaction id and busines paypal token data back to PayPal which responds with SUCCESS or FAILED.
        Returns True if the postback is successful.
        """          
        paypal_response = ""
        postback_dict={}    
        postback_dict["cmd"]="_notify-synch"
        postback_dict["at"]=settings.PAYPAL_IDENTITY_TOKEN    
        postback_dict["tx"]=self.tx    
        postback_params=urlencode(postback_dict)
        
        PP_URL = POSTBACK_ENDPOINT
        if settings.DEBUG:
            PP_URL = SANDBOX_POSTBACK_ENDPOINT
    
        if hasattr(settings, 'PAYPAL_TESTING'):
            client = Client()
            paypal_http_response = client.get(reverse('paypal-fake-pdt-response'), {'custom': self.cm, 'txn_id': self.tx, 'mc_gross': self.amt})
            paypal_response = paypal_http_response.content
        else:
            req = urllib2.Request(PP_URL)
            req.add_header("Content-type", "application/x-www-form-urlencoded")
            fo = urllib2.urlopen(PP_URL, postback_params)
            paypal_response = fo.read()
            fo.close()
            
        logging.info(paypal_response)
        
        SUCCESS = self._parse_paypal_response(paypal_response)
        return SUCCESS
    
    def _parse_paypal_response(self, paypal_response):
        from forms import PayPalPDTForm
        SUCCESS = False
        paypal_response_list = paypal_response.split('\n')
    
        paypal_response_dict = {}
        i = 0
        for paypal_line in paypal_response_list:
            unquoted_paypal_line = unquote_plus(paypal_line)        
            if i == 0:
                self.st = unquoted_paypal_line.strip()
            else:
                if self.st == 'SUCCESS':
                    SUCCESS = True
                    try:
                        
                        [k, v] = unquoted_paypal_line.split('=')                        
                        paypal_response_dict[k.strip()]=v.strip()
                    except ValueError, e:
                        logging.error("comfirm_pay_pal error, %s, %s"%(e, unquoted_paypal_line))
                else:
                    self.flag_info += paypal_line
                    logging.error('transaction_status = %s'%self.st)
            i = i + 1  
        
        q = QueryDict('')
        fake_query_dict = q.copy() # QueryDict instances are immutable so we need to make a copy()
        fake_query_dict.update(paypal_response_dict)
        fake_query_dict.update({'ipaddress': self.ipaddress, 'st': self.st, 'flag_info': self.flag_info})
        pdt_form = PayPalPDTForm(fake_query_dict, instance=self)
        pdt_form.save()
        
        return SUCCESS
    
    def verify(self, item_check_callable=None, test=True):
        """
        Posts back PDT variables to get transaction status
        """        
        from paypal.standard.helpers import duplicate_txn_id
        if not settings.PAYPAL_IDENTITY_TOKEN:
            raise Exception("You must set settings.PAYPAL_IDENTITY_TOKEN in settings.py, you can get this token by enabling PDT in your paypal business account")
        
        success = self._postback(test) 
        if success:
            if self.is_transaction():
                if self.payment_status != "Completed":
                    self.set_flag("Invalid payment_status.")
                if duplicate_txn_id(self, 1): # we have already saved our instance once in parsing the paypal response so our transaction exists
                    self.set_flag("Duplicate transaction ID.")
                if self.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
                    self.set_flag("Invalid receiver_email.")
                if callable(item_check_callable):
                    flag, reason = item_check_callable(self)
                    if flag:
                        self.set_flag(reason)
        else:
            self.set_flag("FAIL")
            
        self.save()        
        if success:
            pdt_successful.send(sender=self)
        else:
            pdt_failed.send(sender=self)        
                    
    
    def __unicode__(self):
        fmt = u"<PDT: %s %s>"
        if self.is_transaction():
            return fmt % ("Transaction", self.txn_id)
        else:
            return fmt % ("Recurring", self.recurring_payment_id)
    