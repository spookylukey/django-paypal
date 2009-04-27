from django.dispatch import Signal

# Sent when a PDT is marked as SUCCESS.
pdt_successful = Signal()

# Sent when a PDT is marked as FAILED.
pdt_failed = Signal()