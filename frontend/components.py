from dataclasses import dataclass
from html import escape
from typing import List, Sequence, Tuple

import streamlit as st

from clients.health_probe import ServiceHealth
from clients.wire_inspector import WireFootprint
from frontend.formatters import NumberFormatter
from frontend.i18n import Translator


@dataclass(frozen=True)
class Stat:
    label: str
    value: str
    hint: str = ""
    alert: bool = False


@dataclass(frozen=True)
class BoardEntry:
    name: str
    price: str
    change: str
    trend: str


class HtmlComponents:
    def __init__(self, translator: Translator, formatter: NumberFormatter):
        self._t = translator
        self._f = formatter

    def render(self, markup: str) -> None:
        st.markdown(markup, unsafe_allow_html=True)

    def masthead(self, services: Sequence[Tuple[str, ServiceHealth]]) -> None:
        stations = "".join(self._station(label, health) for label, health in services)
        self.render(
            f'<section class="ag-masthead"><div><h1>{escape(self._t.t("page.heading"))}</h1>'
            f'<p>{escape(self._t.t("page.lede"))}</p></div>'
            f'<div class="ag-stations" role="status">{stations}</div></section>'
        )

    def _station(self, label: str, health: ServiceHealth) -> str:
        state = "on" if health.serving else "off"
        text = self._t.t("page.serving") if health.serving else self._t.t("page.down")
        return (
            f'<div class="ag-station"><i class="ag-dot {state}"></i>'
            f'<div><b>{escape(label)}</b><small>{escape(health.address)}</small></div>'
            f'<span class="state {state}">{text}</span></div>'
        )

    def caption(self, text: str) -> None:
        self.render(f'<p class="ag-section-caption">{escape(text)}</p>')

    def empty(self, text: str) -> None:
        self.render(f'<div class="ag-empty">{escape(text)}</div>')

    def quote(self, name: str, origin: str, product_id: str, price: str, unit: str,
              trend: str, change: str, facts: Sequence[Tuple[str, str]]) -> None:
        rows = "".join(f"<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>" for k, v in facts)
        arrow = {"up": "▲", "down": "▼", "stable": "■"}[trend]
        self.render(
            f'<article class="ag-quote"><p class="name">{escape(name)}</p>'
            f'<p class="meta">{escape(self._t.t("pricing.origin"))}: {escape(origin)} &nbsp;|&nbsp; <code>{escape(product_id)}</code></p>'
            f'<div class="price">{escape(price)}<small>{escape(self._t.t("pricing.per"))} {escape(unit)}</small></div>'
            f'<span class="ag-change {trend}">{arrow} {escape(change)}</span>'
            f'<dl class="ag-facts">{rows}</dl></article>'
        )

    def wire(self, groups: Sequence[Tuple[str, WireFootprint]], headline: WireFootprint) -> None:
        scale = max(max(fp.json_bytes, fp.protobuf_bytes) for _, fp in groups) or 1
        body = "".join(self._wire_group(label, fp, scale) for label, fp in groups)
        self.render(
            f'<section class="ag-wire"><h4>{escape(self._t.t("wire.title"))}</h4>'
            f'<div class="lead"><strong>{escape(self._f.number(headline.saving_percent, 1))} %</strong>'
            f'<span>{escape(self._t.t("wire.saving"))} ({escape(self._f.number(headline.ratio, 2))}x)</span></div>'
            f'{body}</section>'
        )

    def _wire_group(self, label: str, footprint: WireFootprint, scale: int) -> str:
        return (
            f'<div class="group"><div class="group-label">{escape(label)}</div>'
            f'{self._bar(self._t.t("wire.protobuf"), footprint.protobuf_bytes, scale, "pb")}'
            f'{self._bar(self._t.t("wire.json"), footprint.json_bytes, scale, "js")}</div>'
        )

    def _bar(self, label: str, value: int, scale: int, kind: str) -> str:
        width = max(value / scale * 100, 1.5)
        return (
            f'<div class="ag-bar"><span>{escape(label)}</span>'
            f'<div class="track"><div class="fill {kind}" style="width:{width:.1f}%"></div></div>'
            f'<span class="value">{escape(self._f.bytes(value))}</span></div>'
        )

    def stats(self, items: List[Stat]) -> None:
        cells = "".join(
            f'<div class="ag-stat{" alert" if s.alert else ""}"><dt>{escape(s.label)}</dt>'
            f'<dd>{escape(s.value)}{f"<small>{escape(s.hint)}</small>" if s.hint else ""}</dd></div>'
            for s in items
        )
        self.render(f'<dl class="ag-stats">{cells}</dl>')

    def board(self, entries: Sequence[BoardEntry]) -> None:
        tiles = "".join(
            f'<div class="ag-tile {e.trend}"><b>{escape(e.name)}</b>'
            f'<div class="v">{escape(e.price)}</div><small>{escape(e.change)}</small></div>'
            for e in entries
        )
        self.render(f'<div class="ag-board">{tiles}</div>')

    def table(self, headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
        head = "".join(f"<th>{escape(h)}</th>" for h in headers)
        body = "".join("<tr>" + "".join(f"<td>{escape(c)}</td>" for c in row) + "</tr>" for row in rows)
        self.render(f'<div class="ag-table-wrap"><table class="ag-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
