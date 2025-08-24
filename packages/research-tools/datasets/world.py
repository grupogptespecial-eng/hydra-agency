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


class DatasetsWorldWorldBank(ResearchTool):
    """Fetch macro or development indicators from the World Bank API."""

    def __init__(self) -> None:
        super().__init__(
            name="DatasetsWorldWorldBank",
            category="search",
            scope="world",
            inputs_schema={"country_code", "series", "start_year?", "end_year?"},
            output_schema="dataset",
            providers=[],
            ttl="7d",
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
            base_url="https://api.worldbank.org/v2",
        )

    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:  # noqa: D401
        params = {
            "date": self.span_years(ctx.get("start_year", 2010), ctx.get("end_year", 2025)),
            "format": "json",
        }
        url = f"{self.base_url}/country/{ctx['country_code']}/indicator/{ctx['series']}?{urlencode(params)}"
        return self._request_json(url)

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D401
        rows = raw[1] if isinstance(raw, list) and len(raw) > 1 else []
        items = []
        for r in rows:
            date = r.get("date")
            value = r.get("value")
            items.append(
                {
                    "country": r.get("country", {}).get("id"),
                    "indicator": r.get("indicator", {}).get("id"),
                    "date": int(date) if date else None,
                    "value": value,
                    "unit": r.get("unit"),
                }
            )
        meta = raw[0] if isinstance(raw, list) else {}
        return {"items": items, "meta": meta}


__all__ = ["DatasetsWorldWorldBank"]
