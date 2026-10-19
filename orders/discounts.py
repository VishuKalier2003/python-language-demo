from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Coupon:
    code: str
    percent_off: int = 0
    amount_off: int = 0
    min_subtotal: int = 0
    category: Optional[str] = None


# Mocked coupon book.
MOCK_COUPONS = {
    "WELCOME10": Coupon(code="WELCOME10", percent_off=10),
    "GREEN20": Coupon(code="GREEN20", percent_off=20, category="plants"),
    "SAVE50": Coupon(code="SAVE50", amount_off=50, min_subtotal=500),
}


def find_coupon(code: Optional[str]) -> Optional[Coupon]:
    if not code:
        return None
    return MOCK_COUPONS.get(code.strip().upper())


def discount_for(coupon: Optional[Coupon], lines: list) -> int:
    if coupon is None:
        return 0
    if coupon.category is None:
        eligible = sum(line.line_total for line in lines)
    else:
        eligible = sum(line.line_total for line in lines if line.product.category == coupon.category)
    subtotal = sum(line.line_total for line in lines)
    if eligible == 0 or subtotal < coupon.min_subtotal:
        return 0
    discount = eligible * coupon.percent_off // 100 + coupon.amount_off
    return min(discount, eligible)
