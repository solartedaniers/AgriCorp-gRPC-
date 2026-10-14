import argparse
import logging
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc

ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class ManagedService:
    name: str
    module: str
    address: str


class ProcessOrchestrator:
    def __init__(self, services: List[ManagedService], frontend_port: Optional[int]):
        self._services = services
        self._frontend_port = frontend_port
        self._processes: List[subprocess.Popen] = []
        self._logger = logging.getLogger("launcher")

    def run(self) -> int:
        self._install_signal_handlers()
        try:
            for service in self._services:
                self._spawn(service.name, [sys.executable, "-m", service.module])
            for service in self._services:
                self._wait_until_serving(service)
            if self._frontend_port is None:
                return self._supervise()
            frontend = self._spawn("Dashboard", [
                sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"),
                f"--server.port={self._frontend_port}",
                "--server.address=0.0.0.0",
                "--server.headless=true",
            ])
            return frontend.wait()
        finally:
            self._shutdown()

    def _spawn(self, name: str, command: List[str]) -> subprocess.Popen:
        env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONUNBUFFERED": "1"}
        process = subprocess.Popen(command, cwd=ROOT, env=env)
        self._processes.append(process)
        self._logger.info("%s started as independent process (pid %s)", name, process.pid)
        return process

    def _wait_until_serving(self, service: ManagedService, timeout: float = 30.0) -> None:
        deadline = time.monotonic() + timeout
        with grpc.insecure_channel(service.address) as channel:
            stub = health_pb2_grpc.HealthStub(channel)
            while time.monotonic() < deadline:
                try:
                    status = stub.Check(health_pb2.HealthCheckRequest(), timeout=1).status
                    if status == health_pb2.HealthCheckResponse.SERVING:
                        self._logger.info("%s is SERVING at %s", service.name, service.address)
                        return
                except grpc.RpcError:
                    time.sleep(0.3)
        raise RuntimeError(f"{service.name} did not become healthy at {service.address}")

    def _supervise(self) -> int:
        while all(process.poll() is None for process in self._processes):
            time.sleep(1)
        return 1

    def _install_signal_handlers(self) -> None:
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda *_: sys.exit(0))

    def _shutdown(self) -> None:
        for process in reversed(self._processes):
            if process.poll() is None:
                process.terminate()
        for process in self._processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Starts the gRPC microservices and the dashboard as separate processes")
    parser.add_argument("--services-only", action="store_true")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8501")))
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    arguments = parse_arguments()
    pricing_port = os.getenv("PRICING_PORT", "50051")
    telemetry_port = os.getenv("TELEMETRY_PORT", "50052")
    orchestrator = ProcessOrchestrator(
        services=[
            ManagedService("Pricing Microservice", "services.pricing.server", f"localhost:{pricing_port}"),
            ManagedService("Telemetry Microservice", "services.telemetry.server", f"localhost:{telemetry_port}"),
        ],
        frontend_port=None if arguments.services_only else arguments.port,
    )
    sys.exit(orchestrator.run())
