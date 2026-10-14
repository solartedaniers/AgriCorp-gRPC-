from typing import List

import streamlit as st

from agricultural.v1 import agricultural_market_pb2 as pb2
from clients.errors import ServiceCallError
from clients.settings import ClientSettings
from frontend.components import HtmlComponents
from frontend.formatters import NumberFormatter
from frontend.gateway import ErrorPresenter, ServiceGateway
from frontend.i18n import Translator
from frontend.theme import ThemeInjector
from frontend.views.contract_view import ContractView
from frontend.views.pricing_view import PricingView
from frontend.views.telemetry_view import TelemetryView


@st.cache_resource
def shared_gateway() -> ServiceGateway:
    return ServiceGateway(ClientSettings.from_environment())


class DashboardApp:
    def __init__(self):
        self._t = Translator("es")
        st.set_page_config(page_title=self._t.t("page.title"), page_icon="☕", layout="wide")
        self._gateway = shared_gateway()
        self._formatter = NumberFormatter()
        self._ui = HtmlComponents(self._t, self._formatter)
        self._errors = ErrorPresenter(self._t)

    def render(self) -> None:
        ThemeInjector().apply()
        self._ui.masthead([
            ("Pricing Microservice", self._gateway.pricing.health()),
            ("Telemetry Microservice", self._gateway.telemetry.health()),
        ])
        products = self._load_products()
        pricing_tab, telemetry_tab, contract_tab = st.tabs([
            self._t.t("tabs.pricing"), self._t.t("tabs.telemetry"), self._t.t("tabs.contract"),
        ])
        with pricing_tab:
            PricingView(self._gateway, self._ui, self._t, self._formatter, self._errors).render(products)
        with telemetry_tab:
            TelemetryView(self._gateway, self._ui, self._t, self._formatter, self._errors).render(products)
        with contract_tab:
            ContractView(self._ui, self._t).render()

    def _load_products(self) -> List[pb2.Product]:
        try:
            return self._gateway.pricing.list_products()
        except ServiceCallError as error:
            st.error(self._errors.describe(error, self._gateway.pricing.address))
            return []
