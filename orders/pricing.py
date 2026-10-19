from dataclasses import dataclass
from typing import Optional

from orders.cart import Cart
from orders.discounts import Coupon, discount_for
from orders.shipping import shipping_cost
from payments.fee_by_five_service import calculate_fee
from payments.service import calculate_tax


@dataclass(frozen=True)
class OrderTotals:
    subtotal: int
    discount: int
    fee: int
    tax: int
    shipping: int

    @property
    def total(self) -> int:
        return self.subtotal - self.discount + self.fee + self.tax + self.shipping


def fee_for_cart(cart: Cart) -> int:
    # Fees follow the payments rule: standard lines divide by 10, plants by 5.
    return sum(calculate_fee(line.line_total, line.product.category) for line in cart.lines())


def price_cart(cart: Cart, zone: str, coupon: Optional[Coupon] = None) -> OrderTotals:
    if cart.is_empty():
        raise ValueError("Cannot price an empty cart.")
    lines = cart.lines()
    subtotal = cart.subtotal()
    discount = discount_for(coupon, lines)
    taxable = subtotal - discount
    return OrderTotals(
        subtotal=subtotal,
        discount=discount,
        fee=fee_for_cart(cart),
        tax=round(calculate_tax(taxable)),
        shipping=shipping_cost(zone, cart.total_weight(), taxable),
    )


def format_totals(totals: OrderTotals) -> list:
    return [
        f"Subtotal: {totals.subtotal}",
        f"Discount: -{totals.discount}",
        f"Fee: {totals.fee}",
        f"Tax: {totals.tax}",
        f"Shipping: {totals.shipping}",
        f"Total: {totals.total}",
    ]
