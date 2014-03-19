from django.test import TestCase

from paypal.standard.forms import PayPalPaymentsForm

class PaymentsFormTest(TestCase):

    def test_form_render(self):
        f = PayPalPaymentsForm(initial={'business':'me@mybusiness.com',
                                        'amount': '10.50',
                                        'shipping': '2.00',
                                        })
        self.assertEqual(f.render().strip(), """
<form action="https://www.sandbox.paypal.com/cgi-bin/webscr" method="post">
    <input id="id_business" name="business" type="hidden" value="me@mybusiness.com" /><input id="id_amount" name="amount" type="hidden" value="10.50" /><input id="id_return_url" name="return" type="hidden" /><input id="id_cmd" name="cmd" type="hidden" value="_xclick" /><input id="id_charset" name="charset" type="hidden" value="utf-8" /><input id="id_currency_code" name="currency_code" type="hidden" value="USD" /><input id="id_no_shipping" name="no_shipping" type="hidden" value="1" /><input id="id_shipping" name="shipping" type="hidden" value="2.00" />\n    <input type="image" src="https://www.sandbox.paypal.com/en_US/i/btn/btn_buynowCC_LG.gif" border="0" name="submit" alt="Buy it Now" />
</form>
        """.strip())

    def test_form_endpont(self):
        with self.settings(PAYPAL_TEST=False):
            f = PayPalPaymentsForm(initial={})
            self.assertNotIn('sandbox', f.render())
