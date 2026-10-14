from datetime import datetime, timedelta, timezone


class NumberFormatter:
    COLOMBIA = timezone(timedelta(hours=-5))

    @staticmethod
    def number(value: float, decimals: int = 2) -> str:
        text = f"{value:,.{decimals}f}"
        return text.replace(",", "_").replace(".", ",").replace("_", ".")

    def money(self, value: float, currency: str) -> str:
        prefix = "$ " if currency == "COP" else ""
        return f"{prefix}{self.number(value, 2)}"

    def bytes(self, value: int) -> str:
        if value >= 1024 * 1024:
            return f"{self.number(value / (1024 * 1024), 2)} MB"
        if value >= 1024:
            return f"{self.number(value / 1024, 1)} KB"
        return f"{value} B"

    def percent(self, value: float, signed: bool = False) -> str:
        sign = "+" if signed and value > 0 else ""
        return f"{sign}{self.number(value, 2)} %"

    def milliseconds(self, value: float) -> str:
        return f"{self.number(value, 1)} ms"

    def clock(self, epoch: int) -> str:
        return datetime.fromtimestamp(epoch, self.COLOMBIA).strftime("%H:%M:%S")
