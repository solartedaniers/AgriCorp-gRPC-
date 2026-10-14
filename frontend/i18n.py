import json
from functools import reduce
from pathlib import Path
from typing import Any


class Translator:
    def __init__(self, locale: str = "es"):
        path = Path(__file__).resolve().parent / "locales" / f"{locale}.json"
        self._messages = json.loads(path.read_text(encoding="utf-8"))

    def raw(self, key: str) -> Any:
        return reduce(lambda node, part: node[part], key.split("."), self._messages)

    def t(self, key: str, **values: Any) -> str:
        text = self.raw(key)
        return text.format(**values) if values else text
