#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms


class ValueHiddenInput(forms.HiddenInput):
    """
    Widget that renders only if it has a value.
    Used to remove unused fields from PayPal buttons.
    """

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            return u''
        else:
            return super(ValueHiddenInput, self).render(name, value,
                                                        attrs=attrs,
                                                        renderer=renderer)
