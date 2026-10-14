import grpc
import pytest

from agricultural.v1 import agricultural_market_pb2 as pb2
from clients.errors import ServiceCallError
from clients.iot_station_simulator import IoTStationSimulator, StationProfile
from clients.telemetry_client import TelemetryClientProxy
from clients.wire_inspector import WireInspector


def test_client_stream_aggregates_whole_batch(telemetry_address):
    client = TelemetryClientProxy(telemetry_address, 30, WireInspector())
    packets = IoTStationSimulator(seed=1).generate(StationProfile("ST-1", "CACAO-FINO-02", 22, 65, 1000, 0.5), 2500)
    result = client.stream(packets)
    assert result.summary.processed_records == 2500
    assert result.summary.total_weight_kg == pytest.approx(1000, rel=1e-3)
    assert result.summary.received_bytes == result.stream_footprint.protobuf_bytes
    assert result.stream_footprint.saving_percent > 30


def test_alerts_count_readings_out_of_storage_range(telemetry_address):
    client = TelemetryClientProxy(telemetry_address, 10, WireInspector())
    packets = [
        pb2.TelemetryData(station_id="ST-2", temperature=20, humidity=60, weight_kg=10),
        pb2.TelemetryData(station_id="ST-2", temperature=31, humidity=60, weight_kg=10),
        pb2.TelemetryData(station_id="ST-3", temperature=20, humidity=82, weight_kg=10),
    ]
    summary = client.stream(packets).summary
    assert summary.alert_count == 2
    assert summary.station_count == 2


def test_invalid_packet_aborts_stream(telemetry_address):
    client = TelemetryClientProxy(telemetry_address, 10, WireInspector())
    with pytest.raises(ServiceCallError) as error:
        client.stream([pb2.TelemetryData(station_id="ST-4", temperature=20, humidity=140, weight_kg=1)])
    assert error.value.code == grpc.StatusCode.INVALID_ARGUMENT
