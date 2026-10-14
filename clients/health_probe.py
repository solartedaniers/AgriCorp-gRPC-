from dataclasses import dataclass

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc


@dataclass(frozen=True)
class ServiceHealth:
    name: str
    address: str
    serving: bool
    detail: str


class HealthProbe:
    def __init__(self, channel: grpc.Channel, name: str, address: str, service_name: str):
        self._stub = health_pb2_grpc.HealthStub(channel)
        self._name = name
        self._address = address
        self._service_name = service_name

    def check(self, timeout: float = 1.5) -> ServiceHealth:
        try:
            response = self._stub.Check(health_pb2.HealthCheckRequest(service=self._service_name), timeout=timeout)
            serving = response.status == health_pb2.HealthCheckResponse.SERVING
            status_name = health_pb2.HealthCheckResponse.ServingStatus.Name(response.status)
            return ServiceHealth(self._name, self._address, serving, status_name)
        except grpc.RpcError as error:
            return ServiceHealth(self._name, self._address, False, error.code().name)
