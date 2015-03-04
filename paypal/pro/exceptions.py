class PayPalFailure(Exception):
    def __init__(self, msg, nvp=None):
        super(PayPalFailure, self).__init__(msg)
        self.nvp = nvp
