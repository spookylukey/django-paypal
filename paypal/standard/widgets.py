#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


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


class ReservedValueHiddenInput(ValueHiddenInput):
    """
    Overrides the default name attribute of the form.
    Used for the PayPal `return` field.
    """

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        # Ignore self.build_attrs because its signature
        # has changed between Django versions
        final_attrs = self.attrs.copy()
        final_attrs['type'] = self.input_type
        final_attrs.update(attrs)
        if value != '':
            final_attrs['value'] = force_text(value)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))
