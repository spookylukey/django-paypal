#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST

from paypal.standard.forms import *
from paypal.standard.models import PayPalIPN


@require_POST
def ipn(request, item_check_callable=None):
    """
    PayPal IPN endpoint (notify_url).
    
    """
    form = PayPalIPNForm(request.POST)
    failed = False    
    if form.is_valid():
        try:
            ipn_obj = form.save(commit=False)
        except Exception, e:
            failed = True
    else:
        failed = True
        
    if failed:
        ipn_obj = PayPalIPN.objects.create()
        ipn_obj.set_flag("Invalid form.")
        
    ipn_obj.query = request.POST.urlencode()
    ipn_obj.ip = request.META.get('REMOTE_ADDR', '')

    if not failed:
        # Secrets should only be used over SSL.
        if request.is_secure() and 'secret' in request.GET:
        # if 'secret' in request.GET:
            ipn_obj.verify_secret(form, request.GET['secret'])
        else:
            ipn_obj.verify(item_check_callable)

    ipn_obj.save()    
    return HttpResponse("OKAY")