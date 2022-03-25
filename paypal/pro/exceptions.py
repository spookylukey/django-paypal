class PayPalFailure(Exception):
    def __init__(self, msg, nvp=None):
        super().__init__(msg)
        self.nvp = nvp

    def __str__(self):
        return f"{self.args[0]}, nvp={repr(self.nvp)}"
