"""
Note that sometimes you will get duplicate signals emitted, depending on configuration of your systems.
If you do encounter this, you will need to add the "dispatch_uid" to your connect handlers:
http://code.djangoproject.com/wiki/Signals#Helppost_saveseemstobeemittedtwiceforeachsave

"""

from django.dispatch import Signal

# Sent when a validated, non-duplicated IPN is received.
valid_ipn_received = Signal()

# Sent when a flagged IPN (e.g. duplicate, invalid) is received.
invalid_ipn_received = Signal()
