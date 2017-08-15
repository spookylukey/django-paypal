#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from warnings import warn

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from paypal.standard.conf import (
    BUY_BUTTON_IMAGE, DONATION_BUTTON_IMAGE, PAYPAL_CERT, PAYPAL_CERT_ID, PAYPAL_PRIVATE_CERT, PAYPAL_PUBLIC_CERT,
    POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT, SUBSCRIPTION_BUTTON_IMAGE
)
from paypal.standard.widgets import ReservedValueHiddenInput, ValueHiddenInput
from paypal.utils import warn_untested

log = logging.getLogger(__name__)


# PayPal date format e.g.:
#   20:18:05 Jan 30, 2009 PST
#
# PayPal dates have been spotted in the wild with these formats, beware!
#
# %H:%M:%S %b. %d, %Y PST
# %H:%M:%S %b. %d, %Y PDT
# %H:%M:%S %b %d, %Y PST
# %H:%M:%S %b %d, %Y PDT
#
# To avoid problems with different locales, we don't rely on datetime.strptime,
# which is locale dependent, but do custom parsing in PayPalDateTimeField

MONTHS = [
    'Jan', 'Feb', 'Mar', 'Apr',
    'May', 'Jun', 'Jul', 'Aug',
    'Sep', 'Oct', 'Nov', 'Dec',
]


class PayPalDateTimeField(forms.DateTimeField):

    def to_python(self, value):
        if value in self.empty_values:
            return None

        if isinstance(value, datetime):
            return value

        value = value.strip()

        try:
            time_part, month_part, day_part, year_part, zone_part = value.split()
            month_part = month_part.strip(".")
            day_part = day_part.strip(",")
            month = MONTHS.index(month_part) + 1
            day = int(day_part)
            year = int(year_part)
            hour, minute, second = map(int, time_part.split(":"))
            dt = datetime(year, month, day, hour, minute, second)
        except ValueError as e:
            raise ValidationError(
                _("Invalid date format %(value)s: %(e)s"),
                params={'value': value, 'e': e},
                code="invalid_date"
            )

        if zone_part in ["PDT", "PST"]:
            # PST/PDT is 'US/Pacific'
            dt = timezone.pytz.timezone('US/Pacific').localize(
                dt, is_dst=zone_part == 'PDT')
            if not settings.USE_TZ:
                dt = timezone.make_naive(dt, timezone=timezone.utc)
        return dt


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
    CMD_CHOICES = (
        ("_xclick", "Buy now or Donations"),
        ("_donations", "Donations"),
        ("_cart", "Shopping cart"),
        ("_xclick-subscriptions", "Subscribe")
    )
    SHIPPING_CHOICES = ((1, "No shipping"), (0, "Shipping"))
    NO_NOTE_CHOICES = ((1, "No Note"), (0, "Include Note"))
    RECURRING_PAYMENT_CHOICES = (
        (1, "Subscription Payments Recur"),
        (0, "Subscription payments do not recur")
    )
    REATTEMPT_ON_FAIL_CHOICES = (
        (1, "reattempt billing on Failure"),
        (0, "Do Not reattempt on failure")
    )

    BUY = 'buy'
    SUBSCRIBE = 'subscribe'
    DONATE = 'donate'

    # Where the money goes.
    business = forms.CharField(widget=ValueHiddenInput())

    # Item information.
    amount = forms.IntegerField(widget=ValueHiddenInput())
    item_name = forms.CharField(widget=ValueHiddenInput())
    item_number = forms.CharField(widget=ValueHiddenInput())
    quantity = forms.CharField(widget=ValueHiddenInput())

    # Subscription Related.
    a1 = forms.CharField(widget=ValueHiddenInput())   # Trial 1 Price
    p1 = forms.CharField(widget=ValueHiddenInput())   # Trial 1 Duration
    t1 = forms.CharField(widget=ValueHiddenInput())   # Trial 1 unit of Duration, default to Month
    a2 = forms.CharField(widget=ValueHiddenInput())   # Trial 2 Price
    p2 = forms.CharField(widget=ValueHiddenInput())   # Trial 2 Duration
    t2 = forms.CharField(widget=ValueHiddenInput())   # Trial 2 unit of Duration, default to Month
    a3 = forms.CharField(widget=ValueHiddenInput())   # Subscription Price
    p3 = forms.CharField(widget=ValueHiddenInput())   # Subscription Duration
    t3 = forms.CharField(widget=ValueHiddenInput())   # Subscription unit of Duration, default to Month
    src = forms.CharField(widget=ValueHiddenInput())  # Is billing recurring? default to yes
    sra = forms.CharField(widget=ValueHiddenInput())  # Reattempt billing on failed cc transaction
    no_note = forms.CharField(widget=ValueHiddenInput())
    # Can be either 1 or 2. 1 = modify or allow new subscription creation, 2 = modify only
    modify = forms.IntegerField(widget=ValueHiddenInput())  # Are we modifying an existing subscription?

    # Localization / PayPal Setup
    lc = forms.CharField(widget=ValueHiddenInput())
    page_style = forms.CharField(widget=ValueHiddenInput())
    cbt = forms.CharField(widget=ValueHiddenInput())

    # IPN control.
    notify_url = forms.CharField(widget=ValueHiddenInput())
    cancel_return = forms.CharField(widget=ValueHiddenInput())
    return_url = forms.CharField(widget=ReservedValueHiddenInput(attrs={"name": "return"}))
    custom = forms.CharField(widget=ValueHiddenInput())
    invoice = forms.CharField(widget=ValueHiddenInput())

    # Default fields.
    cmd = forms.ChoiceField(widget=forms.HiddenInput(), initial=CMD_CHOICES[0][0])
    charset = forms.CharField(widget=forms.HiddenInput(), initial="utf-8")
    currency_code = forms.CharField(widget=forms.HiddenInput(), initial="USD")
    no_shipping = forms.ChoiceField(widget=forms.HiddenInput(), choices=SHIPPING_CHOICES,
                                    initial=SHIPPING_CHOICES[0][0])

    def __init__(self, button_type="buy", *args, **kwargs):
        super(PayPalPaymentsForm, self).__init__(*args, **kwargs)
        self.button_type = button_type
        if 'initial' in kwargs:
            kwargs['initial'] = self._fix_deprecated_paypal_receiver_email(kwargs['initial'])
            # Dynamically create, so we can support everything PayPal does.
            for k, v in kwargs['initial'].items():
                if k not in self.base_fields:
                    self.fields[k] = forms.CharField(label=k, widget=ValueHiddenInput(), initial=v)

    def _fix_deprecated_paypal_receiver_email(self, initial_args):
        if 'business' not in initial_args:
            if hasattr(settings, 'PAYPAL_RECEIVER_EMAIL'):
                warn("""The use of the settings.PAYPAL_RECEIVER_EMAIL is Deprecated.
                        The keyword business argument must be given to PayPalPaymentsForm
                        on creation""", DeprecationWarning)
                initial_args['business'] = settings.PAYPAL_RECEIVER_EMAIL
        return initial_args

    def test_mode(self):
        return getattr(settings, 'PAYPAL_TEST', True)

    def get_endpoint(self):
        "Returns the endpoint url for the form."
        if self.test_mode():
            return SANDBOX_POSTBACK_ENDPOINT
        else:
            return POSTBACK_ENDPOINT

    def render(self):
        return format_html(u"""<form action="{0}" method="post">
    {1}
    <input type="image" src="{2}" border="0" name="submit" alt="Buy it Now" />
</form>""", self.get_endpoint(), self.as_p(), self.get_image())

    def sandbox(self):
        "Deprecated.  Use self.render() instead."
        import warnings
        warnings.warn("""PaypalPaymentsForm.sandbox() is deprecated.
                    Use the render() method instead.""", DeprecationWarning)
        return self.render()

    def get_image(self):
        return {
            self.SUBSCRIBE: SUBSCRIPTION_BUTTON_IMAGE,
            self.BUY: BUY_BUTTON_IMAGE,
            self.DONATE: DONATION_BUTTON_IMAGE,
        }[self.button_type]

    def is_transaction(self):
        warn_untested()
        return not self.is_subscription()

    def is_donation(self):
        warn_untested()
        return self.button_type == self.DONATE

    def is_subscription(self):
        warn_untested()
        return self.button_type == self.SUBSCRIBE


class PayPalEncryptedPaymentsForm(PayPalPaymentsForm):
    """
    Creates a PayPal Encrypted Payments "Buy It Now" button.
    Requires the M2Crypto package.

    Based on example at:
    http://blog.mauveweb.co.uk/2007/10/10/paypal-with-django/

    """

    def __init__(self, private_cert=PAYPAL_PRIVATE_CERT, public_cert=PAYPAL_PUBLIC_CERT,
            paypal_cert=PAYPAL_CERT, cert_id=PAYPAL_CERT_ID, *args, **kwargs):
        warn_untested()
        super(PayPalEncryptedPaymentsForm, self).__init__(*args, **kwargs)
        self.private_cert = private_cert
        self.public_cert = public_cert
        self.paypal_cert = paypal_cert
        self.cert_id = cert_id

    def _encrypt(self):
        """Use your key thing to encrypt things."""
        warn_untested()
        from M2Crypto import BIO, SMIME, X509

        # Iterate through the fields and pull out the ones that have a value.
        plaintext = 'cert_id=%s\n' % self.cert_id
        for name, field in self.fields.items():
            value = None
            if name in self.initial:
                value = self.initial[name]
            elif field.initial is not None:
                value = field.initial
            if value is not None:
                # @@@ Make this less hackish and put it in the widget.
                if name == "return_url":
                    name = "return"
                plaintext += u'%s=%s\n' % (name, value)
        plaintext = plaintext.encode('utf-8')

        # Begin crypto weirdness.
        s = SMIME.SMIME()
        s.load_key_bio(BIO.openfile(self.private_cert), BIO.openfile(self.public_cert))
        p7 = s.sign(BIO.MemoryBuffer(plaintext), flags=SMIME.PKCS7_BINARY)
        x509 = X509.load_cert_bio(BIO.openfile(self.paypal_cert))
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
        warn_untested()
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
        warn_untested()
        from paypal.standard.helpers import make_secret

        super(PayPalSharedSecretEncryptedPaymentsForm, self).__init__(*args, **kwargs)
        # @@@ Attach the secret parameter in a way that is safe for other query params.
        secret_param = "?secret=%s" % make_secret(self)
        # Initial data used in form construction overrides defaults
        if 'notify_url' in self.initial:
            self.initial['notify_url'] += secret_param
        else:
            self.fields['notify_url'].initial += secret_param


class PayPalStandardBaseForm(forms.ModelForm):
    """Form used to receive and record PayPal IPN/PDT."""
    # PayPal dates have non-standard formats.
    time_created = PayPalDateTimeField(required=False)
    payment_date = PayPalDateTimeField(required=False)
    next_payment_date = PayPalDateTimeField(required=False)
    subscr_date = PayPalDateTimeField(required=False)
    subscr_effective = PayPalDateTimeField(required=False)
    retry_at = PayPalDateTimeField(required=False)
    case_creation_date = PayPalDateTimeField(required=False)
    auction_closing_date = PayPalDateTimeField(required=False)
