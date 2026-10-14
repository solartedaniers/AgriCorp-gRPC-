import logging
import time

import grpc

from agricultural.v1 import agricultural_market_pb2 as pb2
from agricultural.v1 import agricultural_market_pb2_grpc as pb2_grpc
from services.pricing.catalog_repository import CatalogEntry, PriceCatalogRepository
from services.pricing.market_simulator import MarketSimulator, PriceQuote


class PricingServicer(pb2_grpc.PricingServiceServicer):
    STABLE_THRESHOLD = 0.05

    def __init__(self, repository: PriceCatalogRepository, simulator: MarketSimulator):
        self._repository = repository
        self._simulator = simulator
        self._logger = logging.getLogger("pricing")

    def ListProducts(self, request, context):
        return pb2.ListProductsResponse(products=[self._to_product(e) for e in self._repository.all()])

    def GetProductPrice(self, request, context):
        product_id = request.product_id.strip().upper()
        if not product_id:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "product_id is required")
        entry = self._repository.find(product_id)
        if entry is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Product {product_id} not found in catalog")
        quote = self._simulator.quote(entry)
        self._logger.info("Unary GetProductPrice %s -> %.2f %s", product_id, quote.current, entry.currency)
        return pb2.PriceResponse(
            product_id=entry.product_id,
            current_price=quote.current,
            currency=entry.currency,
            timestamp=int(time.time()),
            previous_price=quote.previous,
            change_percent=round(quote.change_percent, 3),
            trend=self._trend_of(quote),
            product=self._to_product(entry),
        )

    def _trend_of(self, quote: PriceQuote) -> int:
        if abs(quote.change_percent) < self.STABLE_THRESHOLD:
            return pb2.PRICE_TREND_STABLE
        return pb2.PRICE_TREND_UP if quote.change_percent > 0 else pb2.PRICE_TREND_DOWN

    @staticmethod
    def _to_product(entry: CatalogEntry) -> pb2.Product:
        return pb2.Product(
            product_id=entry.product_id,
            name=entry.name,
            unit=entry.unit,
            origin_region=entry.origin_region,
        )
