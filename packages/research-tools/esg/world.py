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


class ESGReportsWorldUNSDG(ResearchTool):
    """Fetches ESG indicator data from the UN SDG API.

    Expects ``series_code`` along with optional ``country_code``,
    ``start_year`` and ``end_year``. Output follows the ``research_bundle``
    schema with items containing ``series``, ``country``, ``year`` and ``value``.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ESGReportsWorldUNSDG",
            category="search",
            scope="world",
            inputs_schema={"series_code", "country_code?", "start_year?", "end_year?"},
            output_schema="research_bundle",
            providers=[],  # call_providers override doesn't use this
            ttl="7d",
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
            base_url="https://unstats.un.org/SDGAPI/v1/sdg/Series/Data",
        )

    # ------------------------------------------------------------------
    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:  # noqa: D401
        params = {
            "seriesCode": ctx["series_code"],
            "timePeriod": self.span_years(ctx.get("start_year", 2010), ctx.get("end_year", 2025)),
        }
        if ctx.get("country_code"):
            params["areaCode"] = ctx["country_code"]
        url = f"{self.base_url}?{urlencode(params)}"
        return self._request_json(url)

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D401
        items = []
        for item in raw.get("data", []):
            year = item.get("timePeriod")
            value = item.get("value")
            items.append(
                {
                    "series": item.get("series") or raw.get("seriesCode"),
                    "country": item.get("geoAreaCode"),
                    "year": int(year) if year else None,
                    "value": float(value) if value not in (None, "") else None,
                    "attributes": item.get("attributes", {}),
                }
            )
        meta = {k: v for k, v in raw.items() if k != "data"}
        return {"items": items, "raw_meta": meta}


__all__ = ["ESGReportsWorldUNSDG"]
