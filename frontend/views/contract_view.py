from pathlib import Path

import streamlit as st

from frontend.components import HtmlComponents
from frontend.i18n import Translator

PROTO_PATH = Path(__file__).resolve().parents[2] / "protos" / "agricultural" / "v1" / "agricultural_market.proto"


class ContractView:
    ARCHITECTURE = """
digraph G {
  rankdir=LR; bgcolor="transparent"; nodesep=0.35; ranksep=0.7;
  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=12, color="#D6DED6", fillcolor="#FFFFFF", fontcolor="#18261E", penwidth=1.2, margin="0.22,0.12"];
  edge [fontname="Helvetica", fontsize=10, color="#5B6A61", fontcolor="#5B6A61"];
  proto [label="agricultural_market.proto\\ncontrato SSOT", fillcolor="#F3EAD9", color="#B8873A"];
  iot [label="Estaciones IoT\\n(simuladas)", fillcolor="#F3F5F1"];
  ui [label="Dashboard Streamlit\\nPricingClientProxy\\nTelemetryClientProxy", fillcolor="#E2EEE6", color="#2F6B4A"];
  pricing [label="Pricing Microservice\\nproceso propio :50051"];
  telemetry [label="Telemetry Microservice\\nproceso propio :50052"];
  repo [label="PriceCatalogRepository\\nMarketSimulator", fillcolor="#F3F5F1"];
  agg [label="TelemetryAggregator\\nStorageConditionPolicy", fillcolor="#F3F5F1"];
  proto -> ui [style=dashed, label="genera stubs"];
  proto -> pricing [style=dashed];
  proto -> telemetry [style=dashed];
  iot -> ui [label="lecturas"];
  ui -> pricing [label="Unary RPC sobre HTTP/2", penwidth=1.6, color="#2F6B4A"];
  ui -> telemetry [label="Client streaming sobre HTTP/2", penwidth=1.6, color="#2F6B4A"];
  pricing -> repo; telemetry -> agg;
}
"""

    def __init__(self, ui: HtmlComponents, translator: Translator):
        self._ui = ui
        self._t = translator

    def render(self) -> None:
        t = self._t.t
        st.subheader(t("contract.architecture"))
        st.graphviz_chart(self.ARCHITECTURE, use_container_width=True)
        left, right = st.columns([1, 1.1], gap="large")
        with left:
            st.subheader(t("contract.title"))
            self._ui.caption(t("contract.caption"))
            st.code(PROTO_PATH.read_text(encoding="utf-8"), language="protobuf", line_numbers=True)
        with right:
            st.subheader(t("contract.rpc_types"))
            self._ui.table(
                [t("contract.method"), t("contract.service"), t("contract.pattern"), t("contract.purpose")],
                [
                    ["ListProducts", "PricingService", t("contract.unary"), t("contract.list_purpose")],
                    ["GetProductPrice", "PricingService", t("contract.unary"), t("contract.price_purpose")],
                    ["StreamTelemetry", "TelemetryService", t("contract.client_streaming"), t("contract.stream_purpose")],
                ],
            )
            st.subheader(t("contract.versus"))
            self._ui.table([t("contract.aspect"), t("contract.rest"), t("contract.grpc")], self._t.raw("contract.rows"))
