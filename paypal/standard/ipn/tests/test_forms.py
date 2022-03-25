import os
import re

from django import forms
from django.test import TestCase

from paypal.standard.forms import (
    PayPalEncryptedPaymentsForm,
    PayPalPaymentsForm,
    PayPalSharedSecretEncryptedPaymentsForm,
)
from paypal.standard.ipn.forms import PayPalIPNForm


class PaymentsFormTest(TestCase):
    def test_form_render(self):
        return_url = "https://example.com/return_url"

        f = PayPalPaymentsForm(
            initial={
                "business": "me@mybusiness.com",
                "amount": "10.50",
                "shipping": "2.00",
                "return_url": return_url,
            }
        )
        rendered = f.render()
        self.assertIn('''action="https://www.sandbox.paypal.com/cgi-bin/webscr"''', rendered)
        self.assertIn('''value="me@mybusiness.com"''', rendered)
        self.assertIn('''value="2.00"''', rendered)
        self.assertIn('''value="10.50"''', rendered)
        self.assertIn("""buynowCC""", rendered)
        self.assertIn('''value="''' + return_url + '''"''', rendered)

        f = PayPalPaymentsForm(
            initial={
                "business": "me@mybusiness.com",
                "amount": "10.50",
                "shipping": "2.00",
                "return": return_url,
            }
        )
        rendered = f.render()
        self.assertIn('''action="https://www.sandbox.paypal.com/cgi-bin/webscr"''', rendered)
        self.assertIn('''value="me@mybusiness.com"''', rendered)
        self.assertIn('''value="2.00"''', rendered)
        self.assertIn('''value="10.50"''', rendered)
        self.assertIn("""buynowCC""", rendered)
        self.assertIn('''value="''' + return_url + '''"''', rendered)

    def test_custom_subclass_form_render(self):
        class CustomAmountPayPalForm(PayPalPaymentsForm):
            """
            PayPal form that lets user choose their own amount
            """

            amount = forms.IntegerField(widget=forms.widgets.NumberInput)

        f = CustomAmountPayPalForm(initial={"business": "me@mybusiness.com"})
        rendered = f.render()
        self.assertIn('<label for="id_amount">Amount:</label>', rendered)
        self.assertIn('<input type="number" name="amount" required id="id_amount">', rendered)
        self.assertIn('value="me@mybusiness.com', rendered)

    def test_form_endpont(self):
        with self.settings(PAYPAL_TEST=False):
            f = PayPalPaymentsForm(initial={})
            self.assertNotIn("sandbox", f.render())

    def test_invalid_date_format(self):
        data = {"payment_date": "2015-10-25 01:21:32"}
        form = PayPalIPNForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            form.errors,
            [
                {"payment_date": ["Invalid date format " "2015-10-25 01:21:32: " "need more than 2 values to unpack"]},
                {
                    "payment_date": [
                        "Invalid date format "
                        "2015-10-25 01:21:32: "
                        "not enough values to unpack "
                        "(expected 5, got 2)"
                    ]
                },
            ],
        )

    def test_encrypted_button(self):
        data = {
            "amount": "10.50",
            "shipping": "2.00",
        }

        # Paypal Certificate Information
        here = os.path.dirname(os.path.abspath(__file__))
        paypal_private_cert = os.path.join(here, "test_cert__do_not_use__private.pem")
        paypal_public_cert = os.path.join(here, "test_cert__do_not_use__public.pem")
        paypal_cert = os.path.join(here, "test_cert_from_paypal__do_not_use.pem")
        paypal_cert_id = "another-paypal-id"

        # Create the instance.
        form = PayPalEncryptedPaymentsForm(
            initial=data,
            private_cert=paypal_private_cert,
            public_cert=paypal_public_cert,
            paypal_cert=paypal_cert,
            cert_id=paypal_cert_id,
        )
        rendered = form.render()

        self.assertIn('''name="cmd" value="_s-xclick"''', rendered)
        self.assertIn("""name="encrypted" value="-----BEGIN PKCS7-----""", rendered)
        expected_regex = re.compile(
            r'.*name="encrypted" value="-----BEGIN PKCS7-----\n'
            + r"([A-Za-z0-9/\+]{64}\n)*[A-Za-z0-9/\+]{1,64}={0,2}\n"
            + r"-----END PKCS7-----\n.*"
        )
        self.assertTrue(
            expected_regex.search(rendered),
            msg="Button encryption has wrong form - expected a block of PKCS7 data",
        )

    def test_shared_secret_encrypted_button(self):
        data = {
            "notify_url": "https://example.com/notify_url",
            "amount": "10.50",
            "shipping": "2.00",
        }

        # Paypal Certificate Information
        here = os.path.dirname(os.path.abspath(__file__))
        paypal_private_cert = os.path.join(here, "test_cert__do_not_use__private.pem")
        paypal_public_cert = os.path.join(here, "test_cert__do_not_use__public.pem")
        paypal_cert = os.path.join(here, "test_cert_from_paypal__do_not_use.pem")
        paypal_cert_id = "another-paypal-id"

        # Create the instance.
        form = PayPalSharedSecretEncryptedPaymentsForm(
            initial=data,
            private_cert=paypal_private_cert,
            public_cert=paypal_public_cert,
            paypal_cert=paypal_cert,
            cert_id=paypal_cert_id,
        )
        rendered = form.render()

        self.assertIn('''name="cmd" value="_s-xclick"''', rendered)
        self.assertIn("""name="encrypted" value="-----BEGIN PKCS7-----""", rendered)
        expected_regex = re.compile(
            r'.*name="encrypted" value="-----BEGIN PKCS7-----\n'
            + r"([A-Za-z0-9/\+]{64}\n)*[A-Za-z0-9/\+]{1,64}={0,2}\n"
            + r"-----END PKCS7-----\n.*"
        )
        self.assertTrue(
            expected_regex.search(rendered),
            msg="Button encryption has wrong form - expected a block of PKCS7 data",
        )
