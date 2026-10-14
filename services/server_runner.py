import logging
import signal
import threading
from concurrent import futures
from typing import Callable

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc


class GrpcServerRunner:
    def __init__(self, name: str, service_name: str, port: int, max_workers: int = 10):
        self._name = name
        self._service_name = service_name
        self._port = port
        self._server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=max_workers),
            options=[
                ("grpc.max_receive_message_length", 16 * 1024 * 1024),
                ("grpc.keepalive_time_ms", 30000),
            ],
        )
        self._health = health.HealthServicer()
        self._stopped = threading.Event()
        self._logger = logging.getLogger(name)

    def register(self, binder: Callable[[grpc.Server], None]) -> "GrpcServerRunner":
        binder(self._server)
        return self

    def start(self) -> None:
        health_pb2_grpc.add_HealthServicer_to_server(self._health, self._server)
        bound_port = self._server.add_insecure_port(f"[::]:{self._port}")
        self._server.start()
        self._health.set(self._service_name, health_pb2.HealthCheckResponse.SERVING)
        self._health.set("", health_pb2.HealthCheckResponse.SERVING)
        self._logger.info("%s listening on port %s (HTTP/2)", self._name, bound_port)

    def stop(self, grace: float = 2.0) -> None:
        if self._stopped.is_set():
            return
        self._stopped.set()
        self._health.enter_graceful_shutdown()
        self._server.stop(grace).wait()
        self._logger.info("%s stopped", self._name)

    def serve_forever(self) -> None:
        self.start()
        self._install_signal_handlers()
        self._server.wait_for_termination()

    def _install_signal_handlers(self) -> None:
        if threading.current_thread() is not threading.main_thread():
            return
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda *_: self.stop())
