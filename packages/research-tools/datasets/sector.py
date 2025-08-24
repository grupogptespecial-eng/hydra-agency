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


class DatasetsSectorFRED(ResearchTool):
    """Fetch sector-level time series from the FRED API."""

    def __init__(self) -> None:
        super().__init__(
            name="DatasetsSectorFRED",
            category="search",
            scope="sector",
            inputs_schema={"series_id", "start_date", "end_date", "frequency?"},
            output_schema="dataset",
            providers=[],
            ttl="7d",
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
            base_url="https://api.stlouisfed.org/fred/series/observations",
            required_env_keys=("FRED_API_KEY",),
            rate_limit_per_sec=5.0,
        )

    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:  # noqa: D401
        env = self._get_env()
        params = {
            "series_id": ctx["series_id"],
            "observation_start": ctx["start_date"],
            "observation_end": ctx["end_date"],
            "api_key": env["FRED_API_KEY"],
            "file_type": "json",
        }
        if ctx.get("frequency"):
            params["frequency"] = ctx["frequency"]
        url = f"{self.base_url}?{urlencode(params)}"
        return self._request_json(url)

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D401
        items = []
        for obs in raw.get("observations", []):
            val = obs.get("value")
            items.append(
                {
                    "series_id": raw.get("series_id") or obs.get("series_id"),
                    "date": obs.get("date"),
                    "value": None if val in (None, ".", "") else float(val),
                }
            )
        return {"items": items, "units": raw.get("units")}


__all__ = ["DatasetsSectorFRED"]
