from django.conf import settings


class PayPalSettingsError(Exception):
    """Raised when settings be bad."""


# API Endpoints.
POSTBACK_ENDPOINT = "https://ipnpb.paypal.com/cgi-bin/webscr"
SANDBOX_POSTBACK_ENDPOINT = "https://ipnpb.sandbox.paypal.com/cgi-bin/webscr"

# Login endpoints
LOGIN_URL = "https://www.paypal.com/cgi-bin/webscr"
SANDBOX_LOGIN_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr"

# Images
BUY_BUTTON_IMAGE = getattr(
    settings,
    "PAYPAL_BUY_BUTTON_IMAGE",
    "https://www.paypal.com/en_US/i/btn/btn_buynowCC_LG.gif",
)
SUBSCRIPTION_BUTTON_IMAGE = getattr(
    settings,
    "PAYPAL_SUBSCRIPTION_BUTTON_IMAGE",
    "https://www.paypal.com/en_US/i/btn/btn_subscribeCC_LG.gif",
)
DONATION_BUTTON_IMAGE = getattr(
    settings,
    "PAYPAL_DONATION_BUTTON_IMAGE",
    "https://www.paypal.com/en_US/i/btn/btn_donateCC_LG.gif",
)


# Paypal Encrypt Certificate
PAYPAL_PRIVATE_CERT = getattr(settings, "PAYPAL_PRIVATE_CERT", None)
PAYPAL_PUBLIC_CERT = getattr(settings, "PAYPAL_PUBLIC_CERT", None)
PAYPAL_CERT = getattr(settings, "PAYPAL_CERT", None)
PAYPAL_CERT_ID = getattr(settings, "PAYPAL_CERT_ID", None)
