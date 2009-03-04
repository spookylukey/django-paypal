#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re        
import datetime

# Adapted from:
# http://www.djangosnippets.org/snippets/764/
# http://www.satchmoproject.com/trac/browser/satchmo/trunk/satchmo/apps/satchmo_utils/views.py
# http://tinyurl.com/shoppify-credit-cards

# Everything that isn't a digit.
RE_NOT_DIGIT = re.compile(r'[^\d]')

# Well known card regular expressions.
CARDS = {
    'Visa': re.compile(r"^4\d{12}(\d{3})?$"),
    'Mastercard': re.compile(r"(5[1-5]\d{4}|677189)\d{10}$"),
    'Dinersclub': re.compile(r"^3(0[0-5]|[68]\d)\d{11}"),
    'Amex': re.compile("^3[47]\d{13}$"),
    'Discover': re.compile("^(6011|65\d{2})\d{12}$"),
}

# Well known test numberss
TEST_NUMBERS = ("378282246310005 371449635398431 378734493671000 30569309025904 38520000023237 6011111111111117 6011000990139424 555555555554444 5105105105105100 4111111111111111 4012888888881881 4222222222222").split()


def verify_credit_card(number):
    """
    Returns the card type for number or None if invalid.
    
    """
    return CreditCard(number).verify()

class CreditCard(object):
    def __init__(self, number):
        self.number = number
	
    def _mod10(self):
        """
        Check a credit card number for validity using the mod10 algorithm.
        
        """
        double = 0
        total = 0
        for i in range(len(self.number) - 1, -1, -1):
            for c in str((double + 1) * int(self.number[i])):
                total = total + int(c)
            double = (double + 1) % 2
        return (total % 10) == 0

    def _strip(self):
        """
        Everything that's not a digit must go.
        
        """
        self.number = RE_NOT_DIGIT.sub('', self.number)
        return self.number.isdigit()

    def _test(self):
        """
        Make sure its not a junk card.
        
        """
        return self.number not in TEST_NUMBERS

    def _type(self):
        """
        Return the type if it matches one of the cards.
        
        """
        for card, pattern in CARDS.iteritems():
            if pattern.match(self.number):
                return card
        return None

    def verify(self):
        """
        Returns the card type if valid else None.
        
        """
        if self._strip() and self._test() and self._mod10():
            return self._type()