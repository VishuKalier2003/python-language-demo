from dataclasses import dataclass, field
from typing import Dict

# Mocked starting stock per SKU.
MOCK_STOCK = {
    "SKU-MUG": 25,
    "SKU-LAMP": 4,
    "SKU-FERN": 10,
    "SKU-CACTUS": 30,
    "SKU-BOOK": 0,
}


@dataclass
class Inventory:
    on_hand: Dict[str, int] = field(default_factory=lambda: dict(MOCK_STOCK))
    reserved: Dict[str, int] = field(default_factory=dict)

    def available(self, sku: str) -> int:
        return self.on_hand.get(sku, 0) - self.reserved.get(sku, 0)

    def can_fulfil(self, quantities: Dict[str, int]) -> bool:
        return all(self.available(sku) >= qty for sku, qty in quantities.items())

    def reserve(self, quantities: Dict[str, int]) -> bool:
        if not self.can_fulfil(quantities):
            return False
        for sku, qty in quantities.items():
            self.reserved[sku] = self.reserved.get(sku, 0) + qty
        return True

    def release(self, quantities: Dict[str, int]) -> None:
        for sku, qty in quantities.items():
            remaining = self.reserved.get(sku, 0) - qty
            if remaining > 0:
                self.reserved[sku] = remaining
            else:
                self.reserved.pop(sku, None)

    def commit(self, quantities: Dict[str, int]) -> None:
        self.release(quantities)
        for sku, qty in quantities.items():
            self.on_hand[sku] = self.on_hand.get(sku, 0) - qty

    def restock(self, sku: str, qty: int) -> None:
        if qty <= 0:
            raise ValueError("Restock quantity must be positive.")
        self.on_hand[sku] = self.on_hand.get(sku, 0) + qty
