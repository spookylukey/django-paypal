from django.dispatch import Signal

# Sent when a payment is successfully processed.
payment_was_successful = Signal(providing_args=["paymentinfo", "response_tokens", "request"])

# Sent when a payment is flagged.
payment_was_flagged = Signal(providing_args=["paymentinfo", "response_tokens", "request"])