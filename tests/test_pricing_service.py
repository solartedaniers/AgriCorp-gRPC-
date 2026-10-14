import grpc
import pytest

from clients.errors import ServiceCallError
from clients.pricing_client import PricingClientProxy
from clients.wire_inspector import WireInspector
from services.pricing.catalog_repository import PriceCatalogRepository
from services.pricing.market_simulator import MarketSimulator


def test_catalog_is_served_from_contract(pricing_address):
    client = PricingClientProxy(pricing_address, 5, WireInspector())
    ids = [product.product_id for product in client.list_products()]
    assert "COFFEE-ARABICA-01" in ids and "CACAO-FINO-02" in ids


def test_unary_price_includes_variation_and_smaller_payload(pricing_address):
    client = PricingClientProxy(pricing_address, 5, WireInspector())
    result = client.get_price("CACAO-FINO-02")
    assert result.response.currency == "COP"
    assert result.response.product.name == "Cacao fino de aroma"
    assert result.response_footprint.protobuf_bytes < result.response_footprint.json_bytes


def test_unknown_product_maps_to_not_found(pricing_address):
    client = PricingClientProxy(pricing_address, 5, WireInspector())
    with pytest.raises(ServiceCallError) as error:
        client.get_price("UNKNOWN-99")
    assert error.value.code == grpc.StatusCode.NOT_FOUND


def test_simulator_stays_within_drift_band():
    entry = PriceCatalogRepository().find("CORN-YELLOW-03")
    simulator = MarketSimulator(seed=7, max_drift=0.1)
    for _ in range(500):
        quote = simulator.quote(entry)
        assert entry.reference_price * 0.9 <= quote.current <= entry.reference_price * 1.1
