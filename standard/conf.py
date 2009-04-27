from django.conf import settings

class PayPalSettingsError(Exception):
    """Raised when settings be bad."""
    
    
def get_or_explode(name, default=None):
    setting = getattr(settings, name, default)
    if setting is None and default is None:
        raise PayPalSettingsError("%s must be set in settings.py" % s)
    else:
        return settings
    
    

TEST = getattr(settings, "PAYPAL_TEST", False)

RECEIVER_EMAIL = get_or_explode("PAYPAL_RECEIVER_EMAIL")


POSTBACK_ENDPOINT = "https://www.paypal.com/cgi-bin/webscr"
SANDBOX_POSTBACK_ENDPOINT = "https://www.sandbox.paypal.com/cgi-bin/webscr"
