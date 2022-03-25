#!/usr/bin/python

from decimal import Decimal

try:
    from unittest import mock
except ImportError:
    from unittest import mock
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from vcr import VCR

from paypal.pro.exceptions import PayPalFailure
from paypal.pro.fields import CreditCardField
from paypal.pro.helpers import VERSION, PayPalError, PayPalWPP, strip_ip_port
from paypal.pro.views import PayPalPro

from .settings import TEMPLATES

RF = RequestFactory()

vcr = VCR(path_transformer=VCR.ensure_suffix(".yaml"))


def make_request(user=None):
    request = RF.get("/pay/", REMOTE_ADDR="127.0.0.1:8000")
    if user is not None:
        request.user = user
    return request


class CreditCardFieldTest(TestCase):
    def test_CreditCardField(self):
        field = CreditCardField()
        field.clean("4797503429879309")
        self.assertEqual(field.card_type, "Visa")
        self.assertRaises(ValidationError, CreditCardField().clean, "1234567890123455")

    def test_invalidCreditCards(self):
        self.assertEqual(CreditCardField().clean("4797-5034-2987-9309"), "4797503429879309")


def ppp_wrapper(request, handler=None):
    item = {
        "paymentrequest_0_amt": "10.00",
        "inv": "inventory",
        "custom": "tracking",
        "cancelurl": "http://foo.com/cancel",
        "returnurl": "http://foo.com/return",
    }

    if handler is None:
        handler = lambda nvp: nvp  # NOP
    ppp = PayPalPro(
        item=item,  # what you're selling
        payment_template="payment.html",  # template name for payment
        confirm_template="confirmation.html",  # template name for confirmation
        success_url="/success/",  # redirect location after success
        nvp_handler=handler,
    )

    return ppp(request)


@override_settings(TEMPLATES=TEMPLATES)
class PayPalProTest(TestCase):
    @vcr.use_cassette()
    def test_get(self):
        response = ppp_wrapper(RF.get("/"))
        self.assertContains(response, "Show me the money")
        self.assertEqual(response.status_code, 200)

    @vcr.use_cassette()
    def test_get_redirect(self):
        response = ppp_wrapper(RF.get("/", {"express": "1"}))
        self.assertEqual(response.status_code, 302)

    @vcr.use_cassette()
    def test_validate_confirm_form_error(self):
        response = ppp_wrapper(RF.post("/", {"token": "123", "PayerID": "456"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get("errors", ""), PayPalPro.errors["processing"])

    @vcr.use_cassette()
    @mock.patch.object(PayPalWPP, "doExpressCheckoutPayment", autospec=True)
    def test_validate_confirm_form_ok(self, doExpressCheckoutPayment):
        nvp = {"mock": True}
        doExpressCheckoutPayment.return_value = nvp

        received = []

        def handler(nvp):
            received.append(nvp)

        response = ppp_wrapper(RF.post("/", {"token": "123", "PayerID": "456"}), handler=handler)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/success/")
        self.assertEqual(len(received), 1)


class PayPalWPPTest(TestCase):
    def setUp(self):

        self.item = {
            "amt": "9.95",
            "inv": "inv",
            "custom": "custom",
            "next": "http://www.example.com/next/",
            "returnurl": "http://www.example.com/pay/",
            "cancelurl": "http://www.example.com/cancel/",
        }
        # Handle different parameters for Express Checkout
        self.ec_item = {
            "paymentrequest_0_amt": "9.95",
            "inv": "inv",
            "custom": "custom",
            "next": "http://www.example.com/next/",
            "returnurl": "http://www.example.com/pay/",
            "cancelurl": "http://www.example.com/cancel/",
        }

    def get_valid_doDirectPayment_data(self):
        return {
            "firstname": "Brave",
            "lastname": "Star",
            "street": "1 Main St",
            "city": "San Jos\xe9",
            "state": "CA",
            "countrycode": "US",
            "zip": "95131",
            "acct": "4032039938039650",
            "expdate": "112021",
            "cvv2": "",
            "creditcardtype": "visa",
            "ipaddress": "10.0.1.199",
        }

    @vcr.use_cassette()
    def test_doDirectPayment_missing_params(self):
        wpp = PayPalWPP(make_request())
        data = {"firstname": "Chewbacca"}
        self.assertRaises(PayPalError, wpp.doDirectPayment, data)

    @vcr.use_cassette()
    def test_doDirectPayment_valid(self):
        wpp = PayPalWPP(make_request())
        data = self.get_valid_doDirectPayment_data()
        data.update(self.item)
        nvp = wpp.doDirectPayment(data)
        self.assertIsNotNone(nvp)
        for k, v in [
            ("avscode", "X"),
            ("amt", "9.95"),
            ("correlationid", "1025431f33d89"),
            ("currencycode", "USD"),
            ("ack", "Success"),
        ]:
            self.assertEqual(nvp.response_dict[k], v)

    @vcr.use_cassette()
    def test_doDirectPayment_authenticated_user(self):
        User = get_user_model()
        user = User.objects.create(username="testuser")
        wpp = PayPalWPP(make_request(user=user))
        data = self.get_valid_doDirectPayment_data()
        data.update(self.item)
        npm_obj = wpp.doDirectPayment(data)
        self.assertEqual(npm_obj.user, user)

    @vcr.use_cassette()
    def test_doDirectPayment_invalid(self):
        wpp = PayPalWPP(make_request())
        data = {
            "firstname": "Epic",
            "lastname": "Fail",
            "street": "100 Georgia St",
            "city": "Vancouver",
            "state": "BC",
            "countrycode": "CA",
            "zip": "V6V 1V1",
            "expdate": "012019",
            "cvv2": "999",
            "acct": "1234567890",
            "creditcardtype": "visa",
            "ipaddress": "10.0.1.199",
        }
        data.update(self.item)
        self.assertRaises(PayPalFailure, wpp.doDirectPayment, data)

    @vcr.use_cassette()
    def test_setExpressCheckout(self):
        wpp = PayPalWPP(make_request())
        nvp_obj = wpp.setExpressCheckout(self.ec_item)
        self.assertEqual(nvp_obj.ack, "Success")

    @vcr.use_cassette()
    @mock.patch.object(PayPalWPP, "_request", autospec=True)
    def test_doExpressCheckoutPayment(self, mock_request_object):
        ec_token = "EC-1234567890"
        payerid = "LXYZABC1234"
        item = self.ec_item.copy()
        item.update({"token": ec_token, "payerid": payerid})
        mock_request_object.return_value = "ack=Success&token={}&version={}paymentinfo_0_amt={}".format(
            ec_token,
            VERSION,
            self.ec_item["paymentrequest_0_amt"],
        )
        wpp = PayPalWPP(make_request())
        wpp.doExpressCheckoutPayment(item)
        call_args = mock_request_object.call_args
        self.assertIn(f"VERSION={VERSION}", call_args[0][1])
        self.assertIn("METHOD=DoExpressCheckoutPayment", call_args[0][1])
        self.assertIn(f"TOKEN={ec_token}", call_args[0][1])
        self.assertIn(f"PAYMENTREQUEST_0_AMT={item['paymentrequest_0_amt']}", call_args[0][1])
        self.assertIn(f"PAYERID={payerid}", call_args[0][1])

    @vcr.use_cassette()
    @mock.patch.object(PayPalWPP, "_request", autospec=True)
    def test_doExpressCheckoutPayment_invalid(self, mock_request_object):
        ec_token = "EC-1234567890"
        payerid = "LXYZABC1234"
        item = self.ec_item.copy()
        item.update({"token": ec_token, "payerid": payerid})
        mock_request_object.return_value = "ack=Failure&l_errorcode=42&l_longmessage0=Broken"
        wpp = PayPalWPP(make_request())
        with self.assertRaises(PayPalFailure):
            wpp.doExpressCheckoutPayment(item)

    @vcr.use_cassette()
    @mock.patch.object(PayPalWPP, "_request", autospec=True)
    def test_createBillingAgreement(self, mock_request_object):
        mock_request_object.return_value = f"ack=Success&billingagreementid=B-XXXXX&version={VERSION}"
        wpp = PayPalWPP(make_request())
        nvp = wpp.createBillingAgreement({"token": "dummy token"})
        call_args = mock_request_object.call_args
        self.assertIn(f"VERSION={VERSION}", call_args[0][1])
        self.assertIn("METHOD=CreateBillingAgreement", call_args[0][1])
        self.assertIn("TOKEN=dummy+token", call_args[0][1])
        self.assertEqual(nvp.method, "CreateBillingAgreement")
        self.assertEqual(nvp.ack, "Success")
        mock_request_object.return_value = "ack=Failure&l_errorcode=42&l_longmessage0=Broken"
        with self.assertRaises(PayPalFailure):
            nvp = wpp.createBillingAgreement({"token": "dummy token"})

    @vcr.use_cassette()
    @mock.patch.object(PayPalWPP, "_request", autospec=True)
    def test_doReferenceTransaction_valid(self, mock_request_object):
        reference_id = "B-1234"
        amount = Decimal("10.50")
        mock_request_object.return_value = (
            "ack=Success&paymentstatus=Completed&amt=%s&version=%s&billingagreementid=%s"
            % (amount, VERSION, reference_id)
        )
        wpp = PayPalWPP(make_request())
        nvp = wpp.doReferenceTransaction({"referenceid": reference_id, "amt": amount})
        call_args = mock_request_object.call_args
        self.assertIn(f"VERSION={VERSION}", call_args[0][1])
        self.assertIn("METHOD=DoReferenceTransaction", call_args[0][1])
        self.assertIn(f"REFERENCEID={reference_id}", call_args[0][1])
        self.assertIn(f"AMT={amount}", call_args[0][1])
        self.assertEqual(nvp.method, "DoReferenceTransaction")
        self.assertEqual(nvp.ack, "Success")

    @vcr.use_cassette()
    @mock.patch.object(PayPalWPP, "_request", autospec=True)
    def test_doReferenceTransaction_invalid(self, mock_request_object):
        reference_id = "B-1234"
        amount = Decimal("10.50")
        mock_request_object.return_value = "ack=Failure&l_errorcode=42&l_longmessage0=Broken"
        wpp = PayPalWPP(make_request())
        with self.assertRaises(PayPalFailure):
            wpp.doReferenceTransaction({"referenceid": reference_id, "amt": amount})

    def test_strip_ip_port(self):
        IPv4 = "192.168.0.1"
        IPv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        PORT = "8000"

        # IPv4 with port
        test = f"{IPv4}:{PORT}"
        self.assertEqual(IPv4, strip_ip_port(test))

        # IPv4 without port
        test = IPv4
        self.assertEqual(IPv4, strip_ip_port(test))

        # IPv6 with port
        test = f"[{IPv6}]:{PORT}"
        self.assertEqual(IPv6, strip_ip_port(test))

        # IPv6 without port
        test = IPv6
        self.assertEqual(IPv6, strip_ip_port(test))

        # No IP
        self.assertEqual("", strip_ip_port(""))


# -- DoExpressCheckoutPayment
# PayPal Request:
# {'amt': '10.00',
#  'cancelurl': u'http://xxx.xxx.xxx.xxx/deploy/480/upgrade/?upgrade=cname',
#  'custom': u'website_id=480&cname=1',
#  'inv': u'website-480-cname',
#  'method': 'DoExpressCheckoutPayment',
#  'next': u'http://xxx.xxx.xxx.xxx/deploy/480/upgrade/?upgrade=cname',
#  'payerid': u'BN5JZ2V7MLEV4',
#  'paymentaction': 'Sale',
#  'returnurl': u'http://xxx.xxx.xxx.xxx/deploy/480/upgrade/?upgrade=cname',
#  'token': u'EC-6HW17184NE0084127'}
#
# PayPal Response:
# {'ack': 'Success',
#  'amt': '10.00',
#  'build': '848077',
#  'correlationid': '375f4773c3d34',
#  'currencycode': 'USD',
#  'feeamt': '0.59',
#  'ordertime': '2009-03-04T20:56:08Z',
#  'paymentstatus': 'Completed',
#  'paymenttype': 'instant',
#  'pendingreason': 'None',
#  'reasoncode': 'None',
#  'taxamt': '0.00',
#  'timestamp': '2009-03-04T20:56:09Z',
#  'token': 'EC-6HW17184NE0084127',
#  'transactionid': '3TG42202A7335864V',
#  'transactiontype': 'expresscheckout',
#  'version': '54.0'}
