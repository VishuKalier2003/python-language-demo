from dataclasses import dataclass

FREE_SHIPPING_THRESHOLD = 1000


@dataclass(frozen=True)
class ShippingZone:
    name: str
    base_rate: int
    per_kg: int


SHIPPING_ZONES = {
    "local": ShippingZone(name="local", base_rate=20, per_kg=5),
    "national": ShippingZone(name="national", base_rate=50, per_kg=10),
    "international": ShippingZone(name="international", base_rate=150, per_kg=25),
}


def find_zone(zone: str) -> ShippingZone:
    normalized = zone.strip().lower()
    if normalized not in SHIPPING_ZONES:
        raise ValueError(f"Shipping zone must be one of: {', '.join(SHIPPING_ZONES)}.")
    return SHIPPING_ZONES[normalized]


def shipping_cost(zone: str, weight_grams: int, subtotal: int) -> int:
    shipping_zone = find_zone(zone)
    if shipping_zone.name != "international" and subtotal >= FREE_SHIPPING_THRESHOLD:
        return 0
    kilograms = -(-weight_grams // 1000)  # round up to the next whole kg
    return shipping_zone.base_rate + shipping_zone.per_kg * kilograms
