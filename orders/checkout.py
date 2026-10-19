from dataclasses import dataclass, field
from typing import Dict, Optional

from auth.flow import authorize
from auth.session import SessionStore
from auth.tokens import MOCK_NOW
from orders.cart import Cart
from orders.discounts import find_coupon
from orders.inventory import Inventory
from orders.pricing import OrderTotals, price_cart

CHECKOUT_ROLE = "payments"


@dataclass
class Order:
    order_id: str
    user_id: str
    items: Dict[str, int]
    totals: OrderTotals
    zone: str
    coupon_code: Optional[str] = None
    status: str = "placed"


@dataclass(frozen=True)
class CheckoutResult:
    ok: bool
    reason: str
    order: Optional[Order] = None


@dataclass
class OrderBook:
    orders: Dict[str, Order] = field(default_factory=dict)
    next_number: int = 1

    def create(self, user_id: str, items: Dict[str, int], totals: OrderTotals, zone: str,
               coupon_code: Optional[str]) -> Order:
        order_id = f"o-{self.next_number:05d}"
        self.next_number += 1
        order = Order(order_id=order_id, user_id=user_id, items=dict(items), totals=totals,
                      zone=zone, coupon_code=coupon_code)
        self.orders[order_id] = order
        return order

    def for_user(self, user_id: str) -> list:
        return [order for order in self.orders.values() if order.user_id == user_id]


def checkout_flow(
    store: SessionStore,
    session_id: str,
    cart: Cart,
    inventory: Inventory,
    book: OrderBook,
    zone: str = "local",
    coupon_code: Optional[str] = None,
    now: int = MOCK_NOW,
) -> CheckoutResult:
    auth = authorize(store, session_id, CHECKOUT_ROLE, now)
    if not auth.ok:
        return CheckoutResult(ok=False, reason=auth.reason)
    if auth.user_id != cart.user_id:
        return CheckoutResult(ok=False, reason="cart_owner_mismatch")
    if cart.is_empty():
        return CheckoutResult(ok=False, reason="empty_cart")

    coupon = find_coupon(coupon_code)
    if coupon_code and coupon is None:
        return CheckoutResult(ok=False, reason="invalid_coupon")

    try:
        totals = price_cart(cart, zone, coupon)
    except ValueError:
        return CheckoutResult(ok=False, reason="invalid_zone")

    if not inventory.reserve(cart.items):
        return CheckoutResult(ok=False, reason="out_of_stock")
    inventory.commit(cart.items)

    order = book.create(cart.user_id, cart.items, totals, zone.strip().lower(),
                        coupon.code if coupon else None)
    cart.clear()
    return CheckoutResult(ok=True, reason="placed", order=order)


def cancel_order(
    store: SessionStore,
    session_id: str,
    order_id: str,
    inventory: Inventory,
    book: OrderBook,
    now: int = MOCK_NOW,
) -> CheckoutResult:
    auth = authorize(store, session_id, CHECKOUT_ROLE, now)
    if not auth.ok:
        return CheckoutResult(ok=False, reason=auth.reason)
    order = book.orders.get(order_id)
    if order is None or order.user_id != auth.user_id:
        return CheckoutResult(ok=False, reason="no_order")
    if order.status != "placed":
        return CheckoutResult(ok=False, reason="not_cancellable", order=order)
    for sku, qty in order.items.items():
        inventory.restock(sku, qty)
    order.status = "cancelled"
    return CheckoutResult(ok=True, reason="cancelled", order=order)
