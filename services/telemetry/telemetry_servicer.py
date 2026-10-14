import logging
import time

import grpc

from agricultural.v1 import agricultural_market_pb2 as pb2
from agricultural.v1 import agricultural_market_pb2_grpc as pb2_grpc
from services.telemetry.storage_policy import StorageConditionPolicy, TelemetryValidator
from services.telemetry.telemetry_aggregator import TelemetryAggregator


class TelemetryServicer(pb2_grpc.TelemetryServiceServicer):
    def __init__(self, policy: StorageConditionPolicy, validator: TelemetryValidator):
        self._policy = policy
        self._validator = validator
        self._logger = logging.getLogger("telemetry")

    def StreamTelemetry(self, request_iterator, context):
        started = time.perf_counter()
        aggregator = TelemetryAggregator(self._policy)
        self._logger.info("Client stream opened by %s", context.peer())
        for packet in request_iterator:
            try:
                self._validator.validate(packet)
            except ValueError as error:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(error))
            aggregator.add(packet)
        state = aggregator.result()
        if state.records == 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "stream closed without telemetry packets")
        elapsed_ms = (time.perf_counter() - started) * 1000
        self._logger.info("Client stream closed: %d packets, %d bytes, %d alerts", state.records, state.received_bytes, state.alerts)
        return pb2.TelemetrySummary(
            processed_records=state.records,
            success=True,
            message=f"Ingested {state.records} packets from {len(state.stations)} station(s) via client streaming",
            avg_temperature=round(state.avg_temperature, 2),
            min_temperature=round(state.min_temperature, 2),
            max_temperature=round(state.max_temperature, 2),
            avg_humidity=round(state.avg_humidity, 2),
            total_weight_kg=round(state.weight_sum, 2),
            alert_count=state.alerts,
            station_count=len(state.stations),
            server_processing_ms=round(elapsed_ms, 3),
            received_bytes=state.received_bytes,
        )
