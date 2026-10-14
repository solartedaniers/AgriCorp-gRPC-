import random
import threading
from dataclasses import dataclass
from typing import Dict, Optional

from services.pricing.catalog_repository import CatalogEntry


@dataclass(frozen=True)
class PriceQuote:
    current: float
    previous: float

    @property
    def change_percent(self) -> float:
        if self.previous == 0:
            return 0.0
        return (self.current - self.previous) / self.previous * 100


class MarketSimulator:
    def __init__(self, seed: Optional[int] = None, max_drift: float = 0.15):
        self._random = random.Random(seed)
        self._last_prices: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._max_drift = max_drift

    def quote(self, entry: CatalogEntry) -> PriceQuote:
        with self._lock:
            previous = self._last_prices.get(entry.product_id, entry.reference_price)
            shock = self._random.gauss(0, entry.volatility)
            candidate = previous * (1 + shock)
            floor = entry.reference_price * (1 - self._max_drift)
            ceiling = entry.reference_price * (1 + self._max_drift)
            current = round(min(max(candidate, floor), ceiling), 2)
            self._last_prices[entry.product_id] = current
            return PriceQuote(current=current, previous=round(previous, 2))
