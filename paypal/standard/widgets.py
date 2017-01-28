#!/usr/bin/env python
# -*- coding: utf-8 -*-
import django
from django import forms
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

try:
    from django.forms.utils import flatatt  # Django 1.7 and later
except ImportError:
    from django.forms.util import flatatt  # earlier


widget_render_takes_renderer = django.VERSION >= (1, 11)


class ValueHiddenInput(forms.HiddenInput):
    """
    Widget that renders only if it has a value.
    Used to remove unused fields from PayPal buttons.
    """

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            return u''
        else:
            if widget_render_takes_renderer:
                return super(ValueHiddenInput, self).render(name, value,
                                                            attrs=attrs,
                                                            renderer=renderer)
            else:
                return super(ValueHiddenInput, self).render(name, value,
                                                            attrs=attrs)


class ReservedValueHiddenInput(ValueHiddenInput):
    """
    Overrides the default name attribute of the form.
    Used for the PayPal `return` field.
    """

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs)
        if value != '':
            final_attrs['value'] = force_text(value)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))
