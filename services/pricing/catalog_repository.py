from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class CatalogEntry:
    product_id: str
    name: str
    unit: str
    origin_region: str
    reference_price: float
    currency: str
    volatility: float


class PriceCatalogRepository:
    def __init__(self, entries: Optional[List[CatalogEntry]] = None):
        source = entries if entries is not None else self._default_entries()
        self._entries: Dict[str, CatalogEntry] = {entry.product_id: entry for entry in source}

    def find(self, product_id: str) -> Optional[CatalogEntry]:
        return self._entries.get(product_id)

    def all(self) -> List[CatalogEntry]:
        return list(self._entries.values())

    @staticmethod
    def _default_entries() -> List[CatalogEntry]:
        return [
            CatalogEntry("COFFEE-ARABICA-01", "Café pergamino seco", "kg", "Nariño", 22500.0, "COP", 0.012),
            CatalogEntry("COFFEE-SPECIALTY-04", "Café especial de altura", "kg", "Nariño", 31800.0, "COP", 0.015),
            CatalogEntry("CACAO-FINO-02", "Cacao fino de aroma", "kg", "Tumaco", 28600.0, "COP", 0.02),
            CatalogEntry("CORN-YELLOW-03", "Maíz amarillo", "kg", "Ipiales", 1450.0, "COP", 0.008),
            CatalogEntry("PANELA-05", "Panela orgánica", "kg", "Sandoná", 4800.0, "COP", 0.006),
        ]
