import sys
from pathlib import Path

import grpc
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.pricing.server import build_runner as build_pricing
from services.telemetry.server import build_runner as build_telemetry


@pytest.fixture(scope="session")
def pricing_address():
    runner = build_pricing(50151)
    runner.start()
    yield "localhost:50151"
    runner.stop(0)


@pytest.fixture(scope="session")
def telemetry_address():
    runner = build_telemetry(50152)
    runner.start()
    yield "localhost:50152"
    runner.stop(0)
