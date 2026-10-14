import logging
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceSettings:
    pricing_port: int
    telemetry_port: int

    @classmethod
    def from_environment(cls) -> "ServiceSettings":
        return cls(
            pricing_port=int(os.getenv("PRICING_PORT", "50051")),
            telemetry_port=int(os.getenv("TELEMETRY_PORT", "50052")),
        )


def configure_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    )
