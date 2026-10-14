import math
import random
import time
from dataclasses import dataclass
from typing import List, Optional

from agricultural.v1 import agricultural_market_pb2 as pb2


@dataclass(frozen=True)
class StationProfile:
    station_id: str
    product_id: str
    base_temperature: float
    base_humidity: float
    lot_weight_kg: float
    sensor_noise: float


class IoTStationSimulator:
    def __init__(self, seed: Optional[int] = None):
        self._random = random.Random(seed)

    def generate(self, profile: StationProfile, readings: int, interval_seconds: int = 60) -> List[pb2.TelemetryData]:
        start = int(time.time()) - readings * interval_seconds
        weight_per_reading = profile.lot_weight_kg / readings
        packets = []
        for index in range(readings):
            daily_cycle = math.sin(2 * math.pi * index / max(readings, 24))
            temperature = profile.base_temperature + 2.5 * daily_cycle + self._random.gauss(0, profile.sensor_noise)
            humidity = profile.base_humidity - 4.0 * daily_cycle + self._random.gauss(0, profile.sensor_noise * 2)
            packets.append(pb2.TelemetryData(
                station_id=profile.station_id,
                temperature=round(temperature, 2),
                humidity=round(min(max(humidity, 0.0), 100.0), 2),
                weight_kg=round(weight_per_reading, 3),
                timestamp=start + index * interval_seconds,
                product_id=profile.product_id,
            ))
        return packets
