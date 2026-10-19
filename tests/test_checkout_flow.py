import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from auth.flow import login_flow
from auth.session import SessionStore
from auth.tokens import MOCK_NOW, TOKEN_TTL
from orders.cart import Cart
from orders.checkout import OrderBook, cancel_order, checkout_flow
from orders.discounts import find_coupon
from orders.inventory import Inventory
from orders.pricing import fee_for_cart, price_cart
from orders.shipping import shipping_cost


def _alice_session():
    store = SessionStore()
    result = login_flow(store, "alice", "alice-pass")
    return store, result.session_id


def test_cart_add_and_subtotal():
    cart = Cart(user_id="u-001")
    cart.add("sku-mug", 2)
    cart.add("SKU-FERN")
    assert cart.items == {"SKU-MUG": 2, "SKU-FERN": 1}
    assert cart.subtotal() == 540


def test_cart_rejects_unknown_and_bad_quantity():
    cart = Cart(user_id="u-001")
    for sku, qty in (("SKU-NOPE", 1), ("SKU-MUG", 0), ("SKU-MUG", 21)):
        try:
            cart.add(sku, qty)
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_fee_uses_category_divisor():
    cart = Cart(user_id="u-001")
    cart.add("SKU-MUG", 1)    # standard 120 -> fee 12
    cart.add("SKU-FERN", 1)   # plants 300 -> fee 60
    assert fee_for_cart(cart) == 72


def test_coupon_applies_to_category():
    cart = Cart(user_id="u-001")
    cart.add("SKU-MUG", 1)
    cart.add("SKU-FERN", 1)
    totals = price_cart(cart, "local", find_coupon("green20"))
    assert totals.discount == 60


def test_free_shipping_threshold():
    assert shipping_cost("national", 1200, 1000) == 0
    assert shipping_cost("national", 1200, 999) == 70
    assert shipping_cost("international", 1200, 5000) == 200


def test_checkout_places_order_and_commits_stock():
    store, session_id = _alice_session()
    cart = Cart(user_id="u-001")
    cart.add("SKU-LAMP", 2)
    inventory = Inventory()
    book = OrderBook()
    result = checkout_flow(store, session_id, cart, inventory, book, zone="national", coupon_code="SAVE50")
    assert result.ok and result.order.order_id == "o-00001"
    assert result.order.totals.discount == 50
    assert inventory.available("SKU-LAMP") == 2
    assert cart.is_empty()


def test_checkout_out_of_stock():
    store, session_id = _alice_session()
    cart = Cart(user_id="u-001")
    cart.add("SKU-BOOK", 1)
    result = checkout_flow(store, session_id, cart, Inventory(), OrderBook())
    assert result.reason == "out_of_stock"
    assert not cart.is_empty()


def test_checkout_requires_payments_role():
    store = SessionStore()
    session_id = login_flow(store, "bob", "bob-pass").session_id
    cart = Cart(user_id="u-002")
    cart.add("SKU-MUG")
    assert checkout_flow(store, session_id, cart, Inventory(), OrderBook()).reason == "forbidden"


def test_checkout_rejects_invalid_coupon_and_expired_session():
    store, session_id = _alice_session()
    cart = Cart(user_id="u-001")
    cart.add("SKU-MUG")
    assert checkout_flow(store, session_id, cart, Inventory(), OrderBook(), coupon_code="BOGUS").reason == "invalid_coupon"
    later = MOCK_NOW + TOKEN_TTL
    assert checkout_flow(store, session_id, cart, Inventory(), OrderBook(), now=later).reason == "no_session"


def test_cancel_order_restocks():
    store, session_id = _alice_session()
    cart = Cart(user_id="u-001")
    cart.add("SKU-CACTUS", 5)
    inventory = Inventory()
    book = OrderBook()
    order = checkout_flow(store, session_id, cart, inventory, book).order
    assert inventory.available("SKU-CACTUS") == 25
    assert cancel_order(store, session_id, order.order_id, inventory, book).reason == "cancelled"
    assert inventory.available("SKU-CACTUS") == 30
    assert cancel_order(store, session_id, order.order_id, inventory, book).reason == "not_cancellable"
