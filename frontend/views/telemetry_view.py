from typing import List, Optional

import altair as alt
import pandas as pd
import streamlit as st

from agricultural.v1 import agricultural_market_pb2 as pb2
from clients.errors import ServiceCallError
from clients.iot_station_simulator import StationProfile
from clients.telemetry_client import StreamCallResult
from frontend.components import HtmlComponents, Stat
from frontend.formatters import NumberFormatter
from frontend.gateway import ErrorPresenter, ServiceGateway
from frontend.i18n import Translator


class TelemetryView:
    RESULT_KEY = "last_stream_result"
    READINGS_KEY = "last_stream_readings"
    STATIONS = {
        "STATION_PASTO_NORTE": "Bodega Pasto Norte",
        "STATION_LA_UNION_02": "Centro de acopio La Unión",
        "STATION_SANDONA_03": "Trapiche Sandoná",
        "STATION_TUMACO_04": "Planta de cacao Tumaco",
    }
    MAX_TEMPERATURE = 28.0
    MAX_HUMIDITY = 75.0

    def __init__(self, gateway: ServiceGateway, ui: HtmlComponents, translator: Translator,
                 formatter: NumberFormatter, errors: ErrorPresenter):
        self._gateway = gateway
        self._ui = ui
        self._t = translator
        self._f = formatter
        self._errors = errors

    def render(self, products: List[pb2.Product]) -> None:
        controls, result = st.columns([1, 1.45], gap="large")
        with controls:
            profile, readings = self._render_controls(products)
        if profile is not None:
            self._stream(profile, readings)
        with result:
            self._render_result(st.session_state.get(self.RESULT_KEY))
        self._render_chart(st.session_state.get(self.READINGS_KEY))

    def _render_controls(self, products: List[pb2.Product]):
        with st.container(border=True):
            st.subheader(self._t.t("telemetry.title"))
            self._ui.caption(self._t.t("telemetry.caption"))
            station_id = st.selectbox(self._t.t("telemetry.station"), list(self.STATIONS), format_func=lambda s: f"{self.STATIONS[s]}  ({s})")
            names = {p.product_id: p.name for p in products} or {"COFFEE-ARABICA-01": "COFFEE-ARABICA-01"}
            product_id = st.selectbox(self._t.t("telemetry.product"), list(names), format_func=names.get)
            readings = st.slider(self._t.t("telemetry.readings"), 10, 5000, 1000, step=10)
            left, right = st.columns(2)
            with left:
                temperature = st.slider(self._t.t("telemetry.base_temperature"), 12.0, 34.0, 22.0, step=0.5)
                noise = st.slider(self._t.t("telemetry.noise"), 0.1, 3.0, 0.8, step=0.1)
            with right:
                humidity = st.slider(self._t.t("telemetry.base_humidity"), 40.0, 95.0, 68.0, step=0.5)
                weight = st.number_input(self._t.t("telemetry.weight"), min_value=10.0, max_value=100000.0, value=1250.0, step=50.0)
            submitted = st.button(self._t.t("telemetry.send"), type="primary", use_container_width=True)
        if not submitted:
            return None, readings
        return StationProfile(station_id, product_id, temperature, humidity, weight, noise), readings

    def _stream(self, profile: StationProfile, readings: int) -> None:
        packets = self._gateway.simulator.generate(profile, readings)
        with st.spinner(self._t.t("telemetry.sending")):
            try:
                result = self._gateway.telemetry.stream(packets)
            except ServiceCallError as error:
                st.error(self._errors.describe(error, self._gateway.telemetry.address))
                return
        st.session_state[self.RESULT_KEY] = result
        st.session_state[self.READINGS_KEY] = pd.DataFrame(
            {
                "lectura": range(1, len(packets) + 1),
                "temperatura": [p.temperature for p in packets],
                "humedad": [p.humidity for p in packets],
            }
        )

    def _render_result(self, result: Optional[StreamCallResult]) -> None:
        if result is None:
            self._ui.empty(self._t.t("telemetry.empty"))
            return
        s = result.summary
        f = self._f
        self._ui.stats([
            Stat(self._t.t("telemetry.processed"), f.number(s.processed_records, 0), f"{s.station_count} {'estación' if s.station_count == 1 else 'estaciones'}"),
            Stat(self._t.t("telemetry.avg_temperature"), f"{f.number(s.avg_temperature, 1)} °C",
                 f'{self._t.t("telemetry.range")} {f.number(s.min_temperature, 1)} a {f.number(s.max_temperature, 1)} °C'),
            Stat(self._t.t("telemetry.avg_humidity"), f"{f.number(s.avg_humidity, 1)} %"),
            Stat(self._t.t("telemetry.total_weight"), f"{f.number(s.total_weight_kg, 1)} kg"),
            Stat(self._t.t("telemetry.alerts"), f.number(s.alert_count, 0),
                 f.percent(s.alert_count / s.processed_records * 100), alert=s.alert_count > 0),
            Stat(self._t.t("telemetry.server_time"), f.milliseconds(s.server_processing_ms),
                 f'{self._t.t("telemetry.round_trip")}: {f.milliseconds(result.latency_ms)}'),
        ])
        st.caption(self._t.t("telemetry.alerts_hint"))
        self._ui.wire([(f'{self._t.t("wire.stream")} ({f.number(result.packets_sent, 0)} mensajes)', result.stream_footprint)], result.stream_footprint)
        with st.expander(self._t.t("telemetry.server_message")):
            st.code(self._gateway.inspector.to_json(s), language="json")

    def _render_chart(self, frame: Optional[pd.DataFrame]) -> None:
        if frame is None:
            return
        st.subheader(self._t.t("telemetry.chart"))
        temperature, humidity = st.columns(2, gap="large")
        with temperature:
            st.altair_chart(self._series(frame, "temperatura", self._t.t("telemetry.temperature"), self.MAX_TEMPERATURE, "#B8873A"), use_container_width=True)
        with humidity:
            st.altair_chart(self._series(frame, "humedad", self._t.t("telemetry.humidity"), self.MAX_HUMIDITY, "#2F6B4A"), use_container_width=True)

    @staticmethod
    def _series(frame: pd.DataFrame, column: str, title: str, limit: float, color: str) -> alt.LayerChart:
        base = alt.Chart(frame).mark_line(strokeWidth=1.4, color=color).encode(
            x=alt.X("lectura:Q", title="Lectura"),
            y=alt.Y(f"{column}:Q", title=title, scale=alt.Scale(zero=False)),
            tooltip=["lectura:Q", alt.Tooltip(f"{column}:Q", format=".2f")],
        )
        rule = alt.Chart(pd.DataFrame({"limite": [limit]})).mark_rule(color="#A8323A", strokeDash=[6, 4], strokeWidth=1.5).encode(y="limite:Q")
        return (base + rule).properties(height=240)
