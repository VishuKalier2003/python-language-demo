from dataclasses import dataclass
from typing import Dict, Optional

from catalog.labels import label

CATEGORIES = ("standard", "plants")


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    category: str
    unit_price: int
    weight_grams: int = 0

    @property
    def display_name(self) -> str:
        return label(self.name)


# Mocked product catalog; prices are whole currency units.
MOCK_PRODUCTS: Dict[str, Product] = {
    "SKU-MUG": Product(sku="SKU-MUG", name="Ceramic Mug", category="standard", unit_price=120, weight_grams=350),
    "SKU-LAMP": Product(sku="SKU-LAMP", name="Desk Lamp", category="standard", unit_price=850, weight_grams=1200),
    "SKU-FERN": Product(sku="SKU-FERN", name="Boston Fern", category="plants", unit_price=300, weight_grams=1500),
    "SKU-CACTUS": Product(sku="SKU-CACTUS", name="Mini Cactus", category="plants", unit_price=90, weight_grams=400),
    "SKU-BOOK": Product(sku="SKU-BOOK", name="Garden Notebook", category="standard", unit_price=60, weight_grams=250),
}


def find_product(sku: str) -> Optional[Product]:
    return MOCK_PRODUCTS.get(sku.strip().upper())


def products_in_category(category: str) -> list:
    normalized = category.strip().lower()
    if normalized not in CATEGORIES:
        raise ValueError(f"Unknown category '{category}'.")
    return [product for product in MOCK_PRODUCTS.values() if product.category == normalized]
