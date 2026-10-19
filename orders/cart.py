from dataclasses import dataclass, field
from typing import Dict, List

from orders.products import Product, find_product

MAX_LINE_QUANTITY = 20


@dataclass(frozen=True)
class CartLine:
    product: Product
    quantity: int

    @property
    def line_total(self) -> int:
        return self.product.unit_price * self.quantity


@dataclass
class Cart:
    user_id: str
    items: Dict[str, int] = field(default_factory=dict)

    def add(self, sku: str, quantity: int = 1) -> None:
        product = find_product(sku)
        if product is None:
            raise ValueError(f"Unknown product '{sku}'.")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive whole number.")
        new_quantity = self.items.get(product.sku, 0) + quantity
        if new_quantity > MAX_LINE_QUANTITY:
            raise ValueError(f"At most {MAX_LINE_QUANTITY} of one product per order.")
        self.items[product.sku] = new_quantity

    def set_quantity(self, sku: str, quantity: int) -> None:
        product = find_product(sku)
        if product is None or product.sku not in self.items:
            raise ValueError(f"'{sku}' is not in the cart.")
        if quantity <= 0:
            del self.items[product.sku]
            return
        if quantity > MAX_LINE_QUANTITY:
            raise ValueError(f"At most {MAX_LINE_QUANTITY} of one product per order.")
        self.items[product.sku] = quantity

    def remove(self, sku: str) -> bool:
        product = find_product(sku)
        if product is None:
            return False
        return self.items.pop(product.sku, None) is not None

    def clear(self) -> None:
        self.items.clear()

    def lines(self) -> List[CartLine]:
        return [CartLine(product=find_product(sku), quantity=qty) for sku, qty in sorted(self.items.items())]

    def is_empty(self) -> bool:
        return not self.items

    def subtotal(self) -> int:
        return sum(line.line_total for line in self.lines())

    def total_weight(self) -> int:
        return sum(line.product.weight_grams * line.quantity for line in self.lines())
