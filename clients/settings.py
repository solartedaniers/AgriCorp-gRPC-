import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ClientSettings:
    pricing_address: str
    telemetry_address: str
    timeout_seconds: float

    @classmethod
    def from_environment(cls) -> "ClientSettings":
        return cls(
            pricing_address=os.getenv("PRICING_SERVICE_ADDR", "localhost:50051"),
            telemetry_address=os.getenv("TELEMETRY_SERVICE_ADDR", "localhost:50052"),
            timeout_seconds=float(os.getenv("GRPC_TIMEOUT_SECONDS", "10")),
        )
