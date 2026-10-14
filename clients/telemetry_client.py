import time
from dataclasses import dataclass
from typing import Iterator, Sequence

import grpc

from agricultural.v1 import agricultural_market_pb2 as pb2
from agricultural.v1 import agricultural_market_pb2_grpc as pb2_grpc
from clients.errors import ServiceCallError
from clients.health_probe import HealthProbe, ServiceHealth
from clients.wire_inspector import WireFootprint, WireInspector

SERVICE_NAME = "agricultural.market.v1.TelemetryService"


@dataclass(frozen=True)
class StreamCallResult:
    summary: pb2.TelemetrySummary
    latency_ms: float
    packets_sent: int
    stream_footprint: WireFootprint


class TelemetryClientProxy:
    def __init__(self, address: str, timeout: float, inspector: WireInspector):
        self._address = address
        self._timeout = timeout
        self._inspector = inspector
        self._channel = grpc.insecure_channel(address)
        self._stub = pb2_grpc.TelemetryServiceStub(self._channel)
        self._probe = HealthProbe(self._channel, "Telemetry", address, SERVICE_NAME)

    @property
    def address(self) -> str:
        return self._address

    def health(self) -> ServiceHealth:
        return self._probe.check()

    def stream(self, packets: Sequence[pb2.TelemetryData]) -> StreamCallResult:
        started = time.perf_counter()
        try:
            summary = self._stub.StreamTelemetry(self._iterate(packets), timeout=self._timeout)
        except grpc.RpcError as error:
            raise ServiceCallError.from_rpc_error("TelemetryService", error) from error
        latency_ms = (time.perf_counter() - started) * 1000
        return StreamCallResult(
            summary=summary,
            latency_ms=latency_ms,
            packets_sent=len(packets),
            stream_footprint=self._inspector.measure_many(packets),
        )

    @staticmethod
    def _iterate(packets: Sequence[pb2.TelemetryData]) -> Iterator[pb2.TelemetryData]:
        yield from packets

    def close(self) -> None:
        self._channel.close()
