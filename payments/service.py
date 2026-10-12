class PaymentService:
    def charge(self, amount):
        return amount + self.fee(amount)

    def refund(self, amount):
        return -amount

    def fee(self, amount):
        return amount // 10


# @crane:selection:1D81J0KB:start
def calculate_tax(amount):
    return amount * 0.18
# @crane:selection:1D81J0KB:end
