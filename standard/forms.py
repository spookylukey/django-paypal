#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from paypal.standard.widgets import ValueHiddenInput, ReservedValueHiddenInput


# API Endpoints. <--- same as endpoints used in standard - can these die?
ENDPOINT = "https://www.paypal.com/cgi-bin/webscr"
SANDBOX_ENDPOINT = "https://www.sandbox.paypal.com/cgi-bin/webscr"
# Images used to render zee buttons
IMAGE = getattr(settings, "PAYPAL_IMAGE", "http://images.paypal.com/images/x-click-but01.gif")
SANDBOX_IMAGE = getattr(settings, "PAYPAL_SANDBOX_IMAGE", "https://www.sandbox.paypal.com/en_US/i/btn/btn_buynowCC_LG.gif")

# 20:18:05 Jan 30, 2009 PST - PST timezone support is not included out of the box.
    # PAYPAL_DATE_FORMAT = ("%H:%M:%S %b. %d, %Y PST", "%H:%M:%S %b %d, %Y PST",)
    # PayPal dates have been spotted in the wild with these formats, beware!
PAYPAL_DATE_FORMAT = ("%H:%M:%S %b. %d, %Y PST",
                      "%H:%M:%S %b. %d, %Y PDT",
                      "%H:%M:%S %b %d, %Y PST",
                      "%H:%M:%S %b %d, %Y PDT",)

class PayPalPaymentsForm(forms.Form):
    """
    Creates a PayPal Payments Standard "Buy It Now" button, configured for a
    selling a single item with no shipping.
    
    For a full overview of all the fields you can set (there is a lot!) see:
    http://tinyurl.com/pps-integration
    
    Usage:
    >>> f = PayPalPaymentsForm(initial={'item_name':'Widget 001', ...})
    >>> f.render()
    u'<form action="https://www.paypal.com/cgi-bin/webscr" method="post"> ...'
    
    """
    # ### ToDo: Add notify_url initial value.
    
    # Choices.
    CMD_CHOIES = (("_xclick", "Buy now or Donations"), ("_cart", "Shopping cart"))
    SHIPPING_CHOIES = ((1, "No shipping"), (0, "Shipping"))
        
    # Where the money goes.
    RECEIVER_EMAIL = settings.PAYPAL_RECEIVER_EMAIL
    business = forms.CharField(widget=ValueHiddenInput(), initial=RECEIVER_EMAIL)

    # Item information.
    amount = forms.IntegerField(widget=ValueHiddenInput())
    item_name = forms.CharField(widget=ValueHiddenInput())
    item_number = forms.CharField(widget=ValueHiddenInput())
    quantity = forms.CharField(widget=ValueHiddenInput())

    # Localization / PayPal Setup
    lc = forms.CharField(widget=ValueHiddenInput())
    page_style = forms.CharField(widget=ValueHiddenInput())
    cbt = forms.CharField(widget=ValueHiddenInput())

    # IPN control.
    notify_url = forms.CharField(widget=ValueHiddenInput()) #, initial=NOTIFY_URL)
    cancel_return = forms.CharField(widget=ValueHiddenInput())
    return_url = forms.CharField(widget=ReservedValueHiddenInput(attrs={"name":"return"}))
    custom = forms.CharField(widget=ValueHiddenInput())
    invoice = forms.CharField(widget=ValueHiddenInput())

    # Default fields.
    cmd = forms.ChoiceField(widget=forms.HiddenInput(), initial=CMD_CHOIES[0][0])
    charset = forms.CharField(widget=forms.HiddenInput(), initial="utf-8")
    currency_code = forms.CharField(widget=forms.HiddenInput(), initial="USD")
    no_shipping = forms.ChoiceField(widget=forms.HiddenInput(), choices=SHIPPING_CHOIES, initial=SHIPPING_CHOIES[0][0])

    def _render(self, endpoint, image):
        return mark_safe(u"""
            <form action="%s" method="post">
                %s
                <input type="image" src="%s" border="0" name="submit" alt="Paypal" />
            </form>
        """ % (endpoint, self.as_p(), image)) 
    
    def render(self):
        return self._render(ENDPOINT, IMAGE)

    def sandbox(self):
        return self._render(SANDBOX_ENDPOINT, SANDBOX_IMAGE)


class PayPalEncryptedPaymentsForm(PayPalPaymentsForm):
    """
    Creates a PayPal Encrypted Payments "Buy It Now" button.
    Requires the M2Crypto package.

    Based on example at:
    http://blog.mauveweb.co.uk/2007/10/10/paypal-with-django/
    
    """
    def _encrypt(self):
        """Use your key thing to encrypt things."""
        from M2Crypto import BIO, SMIME, X509
        CERT = settings.PAYPAL_PRIVATE_CERT
        PUB_CERT = settings.PAYPAL_PUBLIC_CERT
        PAYPAL_CERT = settings.PAYPAL_CERT
        CERT_ID = settings.PAYPAL_CERT_ID

        # Iterate through the fields and pull out the ones that have a value.
        plaintext = 'cert_id=%s\n' % CERT_ID
        for name, field in self.fields.iteritems():
            value = None
            if name in self.initial:
                value = self.initial[name]
            elif field.initial is not None:
                value = field.initial
            if value is not None:
                # ### Todo - make this less hackish and put it in the widget.
                if name == "return_url":
                    name = "return"
                plaintext += u'%s=%s\n' % (name, value)
        plaintext = plaintext.encode('utf-8')
        
    	# Begin crypto weirdness.
    	s = SMIME.SMIME()	
    	s.load_key_bio(BIO.openfile(CERT), BIO.openfile(PUB_CERT))
    	p7 = s.sign(BIO.MemoryBuffer(plaintext), flags=SMIME.PKCS7_BINARY)
    	x509 = X509.load_cert_bio(BIO.openfile(settings.PAYPAL_CERT))
    	sk = X509.X509_Stack()
    	sk.push(x509)
    	s.set_x509_stack(sk)
    	s.set_cipher(SMIME.Cipher('des_ede3_cbc'))
    	tmp = BIO.MemoryBuffer()
    	p7.write_der(tmp)
    	p7 = s.encrypt(tmp, flags=SMIME.PKCS7_BINARY)
    	out = BIO.MemoryBuffer()
    	p7.write(out)	
    	return out.read()
    	
    def as_p(self):
        return mark_safe(u"""
        	<input type="hidden" name="cmd" value="_s-xclick" />
        	<input type="hidden" name="encrypted" value="%s" />            
        """ % self._encrypt())


class PayPalSharedSecretEncryptedPaymentsForm(PayPalEncryptedPaymentsForm):
    """
    Creates a PayPal Encrypted Payments "Buy It Now" button with a Shared Secret.
    Shared secrets should only be used when your IPN endpoint is on HTTPS.
    
    Adds a secret to the notify_url based on the contents of the form.

    """
    def __init__(self, *args, **kwargs):
        "Make the secret from the form initial data and slip it into the form."
        from paypal.standard.helpers import make_secret
        super(PayPalSharedSecretEncryptedPaymentsForm, self).__init__(self, *args, **kwargs)
        # ### ToDo: attach the secret parameter in a way that is safe for other query params.
        secret_param = "?secret=%s" % make_secret(self)
        # Initial data used in form construction overrides defaults
        if 'notify_url' in self.initial:
            self.initial['notify_url'] += secret_param
        else:
            self.fields['notify_url'].initial += secret_param