from payments.service import PaymentService


class FeeByFivePaymentService(PaymentService):
    def fee(self, amount):
        return amount // 5


def calculate_fee(amount, category="standard"):
    if category.strip().lower() == "plants":
        return FeeByFivePaymentService().fee(amount)
    return PaymentService().fee(amount)
