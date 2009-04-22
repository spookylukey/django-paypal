#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.http import require_GET
from paypal.standard.pdt.models import PayPalPDT
from paypal.standard.pdt.forms import PayPalPDTForm


@require_GET
def pdt(request, item_check_callable=None, model_class=PayPalPDT, form_class=PayPalPDTForm):
    """
    Payment data transfer implementation
    https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/howto_html_paymentdatatransfer
    e.g. url
    http://www.yoursite.com/ad/payment/complete?tx=4WJ86550014687441&st=Completed&amt=225.00&cc=EUR&cm=a3e192b8%2d8fea%2d4a86%2db2e8%2dd5bf502e36be&item_number=&sig=LFeVvU3hPqTy6m7mN%2bqarxpZLII%2fiDgNyjBWaxhfWDBFiFW%2b%2bZnW8WzSwbH4Ja8K%2bSXsoQHOlV5V0YtJM%2fVdHaQmXlEWz8endvh2pOiYthgVAH%2bL32OTML1YSJrrQZvz5eF2bo9v0gPasxOwiHgQ%2bzeLos3fU4X2FTw2JxnB%2fQ4%3d
    
    """
    pdt_obj = None
    txn_id = request.GET.get('tx')
    if txn_id is not None:        
        try:
            pdt_obj = model_class.objects.get(txn_id=txn_id)        
        except model_class.DoesNotExist, e:
            # this is a new transaction so we continue processing PDT request
            pass
        
        if pdt_obj is None:
            form = form_class(request.GET)
            failed = False    
            if form.is_valid():
                try:
                    pdt_obj = form.save(commit=False)
                except Exception, e:
                    error = repr(e)
                    failed = True
            else:
                error = form.errors
                failed = True
            
            if failed:
                pdt_obj = model_class()
                pdt_obj.set_flag("Invalid form. %s" % error)
            
            pdt_obj.init(request)
        
            if not failed:
                # The PDT object gets saved during verify
                if pdt_obj.test_ipn:
                    pdt_obj.verify(item_check_callable)
                else:
                    pdt_obj.verify(item_check_callable, test=False)
    else:
        pdt_obj = model_class()
        pdt_obj.set_flag("No transaction id supplied")
        pdt_obj.save()    
 
    context = RequestContext(request, locals())               
    return render_to_response('pdt/pdt.html', context)
