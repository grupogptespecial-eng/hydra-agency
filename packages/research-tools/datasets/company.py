from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import urlencode
import importlib.util
from pathlib import Path

_base_spec = importlib.util.spec_from_file_location(
    "research_tools.base", Path(__file__).resolve().parents[1] / "base.py"
)
_base_module = importlib.util.module_from_spec(_base_spec)
assert _base_spec.loader is not None  # pragma: no cover
_base_spec.loader.exec_module(_base_module)  # type: ignore
ResearchTool = _base_module.ResearchTool  # type: ignore


class DatasetsCompanyAlphaVantage(ResearchTool):
    """Fetch daily stock prices from the Alpha Vantage API."""

    def __init__(self) -> None:
        super().__init__(
            name="DatasetsCompanyAlphaVantage",
            category="search",
            scope="company",
            inputs_schema={"symbol", "adjusted?", "outputsize?"},
            output_schema="dataset",
            providers=[],
            ttl="12h",
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
            base_url="https://www.alphavantage.co/query",
            required_env_keys=("ALPHAVANTAGE_KEY",),
            rate_limit_per_sec=0.2,
        )

    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:  # noqa: D401
        env = self._get_env()
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED" if ctx.get("adjusted", True) else "TIME_SERIES_DAILY",
            "symbol": ctx["symbol"],
            "apikey": env["ALPHAVANTAGE_KEY"],
            "outputsize": ctx.get("outputsize", "compact"),
        }
        url = f"{self.base_url}?{urlencode(params)}"
        return self._request_json(url)

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D401
        key = "Time Series (Daily)"
        ts = raw.get(key) or {}
        items = []
        for date, row in sorted(ts.items()):
            items.append(
                {
                    "symbol": raw.get("Meta Data", {}).get("2. Symbol"),
                    "date": date,
                    "open": float(row.get("1. open", 0)),
                    "high": float(row.get("2. high", 0)),
                    "low": float(row.get("3. low", 0)),
                    "close": float(row.get("4. close", 0)),
                    "volume": float(row.get("6. volume") or row.get("5. volume") or 0),
                }
            )
        return {"items": items}


__all__ = ["DatasetsCompanyAlphaVantage"]
