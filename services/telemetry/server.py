from agricultural.v1 import agricultural_market_pb2_grpc as pb2_grpc
from services.server_runner import GrpcServerRunner
from services.settings import ServiceSettings, configure_logging
from services.telemetry.storage_policy import StorageConditionPolicy, TelemetryValidator
from services.telemetry.telemetry_servicer import TelemetryServicer

SERVICE_NAME = "agricultural.market.v1.TelemetryService"


def build_runner(port: int) -> GrpcServerRunner:
    servicer = TelemetryServicer(StorageConditionPolicy(), TelemetryValidator())
    return GrpcServerRunner("Telemetry Microservice", SERVICE_NAME, port).register(
        lambda server: pb2_grpc.add_TelemetryServiceServicer_to_server(servicer, server)
    )


if __name__ == "__main__":
    configure_logging()
    build_runner(ServiceSettings.from_environment().telemetry_port).serve_forever()
