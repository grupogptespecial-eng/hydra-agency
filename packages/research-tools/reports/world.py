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


class GeneralReportsWorldWDS(ResearchTool):
    """Fetch general development reports from the World Bank WDS API."""

    def __init__(self) -> None:
        super().__init__(
            name="GeneralReportsWorldWDS",
            category="search",
            scope="world",
            inputs_schema={"start_year", "end_year", "q?", "rows?"},
            output_schema="research_bundle",
            providers=[],
            ttl="30d",
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
            base_url="https://documents.worldbank.org/api/v3/search",
        )

    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = {
            "format": "json",
            "start_year": ctx["start_year"],
            "end_year": ctx["end_year"],
            "rows": ctx.get("rows", 50),
        }
        if ctx.get("q"):
            params["q"] = ctx["q"]
        url = f"{self.base_url}?{urlencode(params)}"
        return self._request_json(url)

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        docs = raw.get("documents") or raw.get("result", {}).get("docs", [])
        items = []
        for d in docs:
            items.append(
                {
                    "title": d.get("display_title") or d.get("title"),
                    "year": d.get("disclosure_year") or d.get("publication_year"),
                    "url": d.get("pdfurl") or d.get("doc_url") or d.get("url"),
                    "region": d.get("region"),
                    "topics": d.get("topics"),
                }
            )
        return {"items": items}


__all__ = ["GeneralReportsWorldWDS"]
