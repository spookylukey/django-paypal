import django

if django.VERSION < (1, 6):
    # Old style test discovery
    from .test_ipn import *  # NOQA
    from .test_forms import *  # NOQA
