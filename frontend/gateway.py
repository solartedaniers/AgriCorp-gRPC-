import grpc

from clients.errors import ServiceCallError
from clients.iot_station_simulator import IoTStationSimulator
from clients.pricing_client import PricingClientProxy
from clients.settings import ClientSettings
from clients.telemetry_client import TelemetryClientProxy
from clients.wire_inspector import WireInspector
from frontend.i18n import Translator


class ServiceGateway:
    def __init__(self, settings: ClientSettings):
        self.inspector = WireInspector()
        self.pricing = PricingClientProxy(settings.pricing_address, settings.timeout_seconds, self.inspector)
        self.telemetry = TelemetryClientProxy(settings.telemetry_address, settings.timeout_seconds * 6, self.inspector)
        self.simulator = IoTStationSimulator()


class ErrorPresenter:
    def __init__(self, translator: Translator):
        self._t = translator

    def describe(self, error: ServiceCallError, address: str) -> str:
        if error.code in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED):
            return self._t.t("errors.unavailable", service=error.service, address=address)
        if error.code == grpc.StatusCode.NOT_FOUND:
            return self._t.t("errors.not_found")
        if error.code == grpc.StatusCode.INVALID_ARGUMENT:
            return self._t.t("errors.invalid", details=error.details)
        return self._t.t("errors.generic", code=error.code.name, details=error.details)
