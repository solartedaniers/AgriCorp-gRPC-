import math
from dataclasses import dataclass, field
from typing import Set

from services.telemetry.storage_policy import StorageConditionPolicy


@dataclass
class TelemetryAggregate:
    records: int = 0
    temperature_sum: float = 0.0
    humidity_sum: float = 0.0
    weight_sum: float = 0.0
    min_temperature: float = math.inf
    max_temperature: float = -math.inf
    alerts: int = 0
    received_bytes: int = 0
    stations: Set[str] = field(default_factory=set)

    @property
    def avg_temperature(self) -> float:
        return self.temperature_sum / self.records if self.records else 0.0

    @property
    def avg_humidity(self) -> float:
        return self.humidity_sum / self.records if self.records else 0.0


class TelemetryAggregator:
    def __init__(self, policy: StorageConditionPolicy):
        self._policy = policy
        self._aggregate = TelemetryAggregate()

    def add(self, packet) -> None:
        state = self._aggregate
        state.records += 1
        state.temperature_sum += packet.temperature
        state.humidity_sum += packet.humidity
        state.weight_sum += packet.weight_kg
        state.min_temperature = min(state.min_temperature, packet.temperature)
        state.max_temperature = max(state.max_temperature, packet.temperature)
        state.received_bytes += packet.ByteSize()
        state.stations.add(packet.station_id)
        if self._policy.is_out_of_range(packet.temperature, packet.humidity):
            state.alerts += 1

    def result(self) -> TelemetryAggregate:
        return self._aggregate
