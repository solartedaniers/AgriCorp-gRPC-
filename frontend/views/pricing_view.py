from datetime import datetime
from typing import Dict, List, Optional

import altair as alt
import pandas as pd
import streamlit as st

from agricultural.v1 import agricultural_market_pb2 as pb2
from clients.errors import ServiceCallError
from clients.pricing_client import PriceCallResult
from frontend.components import BoardEntry, HtmlComponents
from frontend.formatters import NumberFormatter
from frontend.gateway import ErrorPresenter, ServiceGateway
from frontend.i18n import Translator


class PricingView:
    HISTORY_KEY = "price_history"
    LAST_KEY = "last_price_result"
    LATEST_KEY = "latest_by_product"
    TREND_CLASS = {pb2.PRICE_TREND_UP: "up", pb2.PRICE_TREND_DOWN: "down"}

    def __init__(self, gateway: ServiceGateway, ui: HtmlComponents, translator: Translator,
                 formatter: NumberFormatter, errors: ErrorPresenter):
        self._gateway = gateway
        self._ui = ui
        self._t = translator
        self._f = formatter
        self._errors = errors
        st.session_state.setdefault(self.HISTORY_KEY, [])
        st.session_state.setdefault(self.LATEST_KEY, {})

    def render(self, products: List[pb2.Product]) -> None:
        if not products:
            st.error(self._t.t("pricing.unavailable"))
            return
        controls, result = st.columns([1, 1.45], gap="large")
        with controls:
            selected = self._render_controls(products)
        with result:
            self._render_result(st.session_state.get(self.LAST_KEY))
        self._render_board(products)
        self._render_history(selected)

    def _render_controls(self, products: List[pb2.Product]) -> pb2.Product:
        with st.container(border=True):
            st.subheader(self._t.t("pricing.title"))
            self._ui.caption(self._t.t("pricing.caption"))
            by_id: Dict[str, pb2.Product] = {p.product_id: p for p in products}
            product_id = st.radio(
                self._t.t("pricing.product"),
                options=list(by_id),
                format_func=lambda pid: f"{by_id[pid].name}  ({by_id[pid].origin_region})",
            )
            if st.button(self._t.t("pricing.query"), type="primary", use_container_width=True):
                self._query([product_id])
            if st.button(self._t.t("pricing.query_all"), use_container_width=True):
                self._query(list(by_id))
                st.session_state[self.LAST_KEY] = st.session_state[self.LATEST_KEY].get(product_id)
            return by_id[product_id]

    def _query(self, product_ids: List[str]) -> None:
        for product_id in product_ids:
            try:
                result = self._gateway.pricing.get_price(product_id)
            except ServiceCallError as error:
                st.error(self._errors.describe(error, self._gateway.pricing.address))
                return
            self._remember(result)

    def _remember(self, result: PriceCallResult) -> None:
        response = result.response
        st.session_state[self.LAST_KEY] = result
        st.session_state[self.LATEST_KEY][response.product_id] = result
        st.session_state[self.HISTORY_KEY].append({
            "product_id": response.product_id,
            "producto": response.product.name,
            "hora": datetime.fromtimestamp(response.timestamp),
            "precio": response.current_price,
            "latencia_ms": round(result.latency_ms, 2),
        })

    def _render_result(self, result: Optional[PriceCallResult]) -> None:
        if result is None:
            self._ui.empty(self._t.t("pricing.empty"))
            return
        response = result.response
        trend = self.TREND_CLASS.get(response.trend, "stable")
        self._ui.quote(
            name=response.product.name,
            origin=response.product.origin_region,
            product_id=response.product_id,
            price=f"{self._f.money(response.current_price, response.currency)} {response.currency}",
            unit=response.product.unit,
            trend=trend,
            change=f"{self._f.percent(response.change_percent, signed=True)}  {self._trend_label(trend)}",
            facts=[
                (self._t.t("pricing.previous"), self._f.money(response.previous_price, response.currency)),
                (self._t.t("pricing.latency"), self._f.milliseconds(result.latency_ms)),
                (self._t.t("pricing.updated"), self._f.clock(response.timestamp)),
            ],
        )
        total = result.request_footprint + result.response_footprint
        self._ui.wire(
            [(self._t.t("wire.request"), result.request_footprint), (self._t.t("wire.response"), result.response_footprint)],
            total,
        )
        with st.expander(self._t.t("wire.show_payload")):
            st.code(self._gateway.inspector.to_json(response), language="json")

    def _trend_label(self, trend: str) -> str:
        return self._t.t(f"pricing.trend_{trend}")

    def _render_board(self, products: List[pb2.Product]) -> None:
        latest: Dict[str, PriceCallResult] = st.session_state[self.LATEST_KEY]
        if not latest:
            return
        st.subheader(self._t.t("pricing.board"))
        entries = []
        for product in products:
            result = latest.get(product.product_id)
            if result is None:
                continue
            response = result.response
            entries.append(BoardEntry(
                name=product.name,
                price=f"{self._f.money(response.current_price, response.currency)} / {product.unit}",
                change=self._f.percent(response.change_percent, signed=True),
                trend=self.TREND_CLASS.get(response.trend, "stable"),
            ))
        self._ui.board(entries)

    def _render_history(self, product: pb2.Product) -> None:
        st.subheader(f'{self._t.t("pricing.history")}: {product.name}')
        history = [row for row in st.session_state[self.HISTORY_KEY] if row["product_id"] == product.product_id]
        if not history:
            self._ui.empty(self._t.t("pricing.history_empty"))
            return
        frame = pd.DataFrame(history)
        chart = alt.Chart(frame).mark_line(point=alt.OverlayMarkDef(size=60, filled=True), strokeWidth=2.5, color="#2F6B4A").encode(
            x=alt.X("hora:T", title=None, axis=alt.Axis(format="%H:%M:%S")),
            y=alt.Y("precio:Q", title="COP", scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip("hora:T", format="%H:%M:%S"), alt.Tooltip("precio:Q", format=",.2f"), "latencia_ms:Q"],
        ).properties(height=260)
        st.altair_chart(chart, use_container_width=True)
