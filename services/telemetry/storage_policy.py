from dataclasses import dataclass


@dataclass(frozen=True)
class StorageConditionPolicy:
    max_temperature: float = 28.0
    max_humidity: float = 75.0

    def is_out_of_range(self, temperature: float, humidity: float) -> bool:
        return temperature > self.max_temperature or humidity > self.max_humidity


class TelemetryValidator:
    def validate(self, packet) -> None:
        if not packet.station_id:
            raise ValueError("station_id is required on every packet")
        if not 0.0 <= packet.humidity <= 100.0:
            raise ValueError(f"humidity {packet.humidity} outside 0-100 range")
        if not -20.0 <= packet.temperature <= 70.0:
            raise ValueError(f"temperature {packet.temperature} outside sensor range")
        if packet.weight_kg < 0:
            raise ValueError("weight_kg cannot be negative")
