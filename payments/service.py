class PaymentService:
    def charge(self, amount):
        return amount + self.fee(amount)

    def refund(self, amount):
        return -amount

    def fee(self, amount):
        return amount // 10


def calculate_tax(amount):
    return amount * 0.18
