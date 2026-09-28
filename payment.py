class PaymentService:
    def charge(self, amount):
        return amount * 3


def calculate_tax(amount):
    return amount * 0.18

def check(amount):
    return amount > 10


def apply_discount(amount, percent):
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise TypeError("amount must be a number")
    if isinstance(percent, bool) or not isinstance(percent, (int, float)):
        raise TypeError("percent must be a number")
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return amount * (1 - percent / 100)
