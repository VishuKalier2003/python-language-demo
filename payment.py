class PaymentService:
    def charge(self, amount):
        return amount * 3


def calculate_tax(amount):
    return amount * 0.18

def check(amount):
    return amount > 10


def _require_number(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")


def apply_discount(original_amount: float, discount_percent: float) -> float:
    _require_number(original_amount, "original_amount")
    _require_number(discount_percent, "discount_percent")
    if original_amount < 0:
        raise ValueError("original_amount must be non-negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")
    return original_amount * (100 - discount_percent) / 100
