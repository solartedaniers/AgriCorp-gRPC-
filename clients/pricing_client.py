import time
from dataclasses import dataclass
from typing import List

import grpc

from agricultural.v1 import agricultural_market_pb2 as pb2
from agricultural.v1 import agricultural_market_pb2_grpc as pb2_grpc
from clients.errors import ServiceCallError
from clients.health_probe import HealthProbe, ServiceHealth
from clients.wire_inspector import WireFootprint, WireInspector

SERVICE_NAME = "agricultural.market.v1.PricingService"


@dataclass(frozen=True)
class PriceCallResult:
    response: pb2.PriceResponse
    latency_ms: float
    request_footprint: WireFootprint
    response_footprint: WireFootprint


class PricingClientProxy:
    def __init__(self, address: str, timeout: float, inspector: WireInspector):
        self._address = address
        self._timeout = timeout
        self._inspector = inspector
        self._channel = grpc.insecure_channel(address)
        self._stub = pb2_grpc.PricingServiceStub(self._channel)
        self._probe = HealthProbe(self._channel, "Pricing", address, SERVICE_NAME)

    @property
    def address(self) -> str:
        return self._address

    def health(self) -> ServiceHealth:
        return self._probe.check()

    def list_products(self) -> List[pb2.Product]:
        try:
            return list(self._stub.ListProducts(pb2.ListProductsRequest(), timeout=self._timeout).products)
        except grpc.RpcError as error:
            raise ServiceCallError.from_rpc_error("PricingService", error) from error

    def get_price(self, product_id: str) -> PriceCallResult:
        request = pb2.PriceRequest(product_id=product_id)
        started = time.perf_counter()
        try:
            response = self._stub.GetProductPrice(request, timeout=self._timeout)
        except grpc.RpcError as error:
            raise ServiceCallError.from_rpc_error("PricingService", error) from error
        latency_ms = (time.perf_counter() - started) * 1000
        return PriceCallResult(
            response=response,
            latency_ms=latency_ms,
            request_footprint=self._inspector.measure(request),
            response_footprint=self._inspector.measure(response),
        )

    def close(self) -> None:
        self._channel.close()
