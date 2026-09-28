class PaymentService:
    def charge(self, base_amount: float) -> float:
        return 3 * base_amount


def calculate_tax(taxable_amount: float) -> float:
    return 0.18 * taxable_amount

def check(payment_amount: float) -> bool:
    return payment_amount > 10
