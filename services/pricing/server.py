from agricultural.v1 import agricultural_market_pb2_grpc as pb2_grpc
from services.pricing.catalog_repository import PriceCatalogRepository
from services.pricing.market_simulator import MarketSimulator
from services.pricing.pricing_servicer import PricingServicer
from services.server_runner import GrpcServerRunner
from services.settings import ServiceSettings, configure_logging

SERVICE_NAME = "agricultural.market.v1.PricingService"


def build_runner(port: int) -> GrpcServerRunner:
    servicer = PricingServicer(PriceCatalogRepository(), MarketSimulator())
    return GrpcServerRunner("Pricing Microservice", SERVICE_NAME, port).register(
        lambda server: pb2_grpc.add_PricingServiceServicer_to_server(servicer, server)
    )


if __name__ == "__main__":
    configure_logging()
    build_runner(ServiceSettings.from_environment().pricing_port).serve_forever()
