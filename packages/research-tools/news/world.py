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


class NewsWorldGDELT(ResearchTool):
    """Fetch world news events from the GDELT Events API."""

    def __init__(self) -> None:
        super().__init__(
            name="NewsWorldGDELT",
            category="search",
            scope="world",
            inputs_schema={"query", "start_datetime", "end_datetime"},
            output_schema="research_bundle",
            providers=[],
            ttl="1d",
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
            base_url="https://api.gdeltproject.org/api/v2/events/query",
        )

    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:  # noqa: D401
        params = {
            "query": ctx["query"],
            "mode": "EventList",
            "startdatetime": ctx["start_datetime"],
            "enddatetime": ctx["end_datetime"],
            "format": "json",
        }
        url = f"{self.base_url}?{urlencode(params)}"
        return self._request_json(url)

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D401
        items = []
        for ev in raw.get("events", []):
            items.append(
                {
                    "date": ev.get("Day") or ev.get("SQLDATE"),
                    "source": ev.get("SOURCEURL"),
                    "country": ev.get("ActionGeo_CountryCode"),
                    "theme": ev.get("Themes"),
                    "actor1": ev.get("Actor1Name"),
                    "actor2": ev.get("Actor2Name"),
                    "tone": ev.get("AvgTone"),
                }
            )
        return {"items": items, "count": len(items)}


__all__ = ["NewsWorldGDELT"]
