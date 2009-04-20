from django.dispatch import Signal

# Sent when a payment is successfully processed.
payment_was_successful = Signal()

# Sent when a payment is flagged.
payment_was_flagged = Signal()

# Sent when a PDT is marked as SUCCESS.
pdt_successful = Signal()

# Sent when a PDT is marked as FAILED.
pdt_failed = Signal()