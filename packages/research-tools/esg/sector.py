from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import urlencode, quote_plus
import importlib.util
from pathlib import Path

_base_spec = importlib.util.spec_from_file_location(
    "research_tools.base", Path(__file__).resolve().parents[1] / "base.py"
)
_base_module = importlib.util.module_from_spec(_base_spec)
assert _base_spec.loader is not None  # pragma: no cover
_base_spec.loader.exec_module(_base_module)  # type: ignore
ResearchTool = _base_module.ResearchTool  # type: ignore


class ESGReportsSectorWikiRate(ResearchTool):
    """Fetches ESG metrics by industry from the WikiRate API."""

    def __init__(self) -> None:
        super().__init__(
            name="ESGReportsSectorWikiRate",
            category="search",
            scope="sector",
            inputs_schema={"metric", "industry", "year?", "country?"},
            output_schema="research_bundle",
            providers=[],
            ttl="7d",
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
            base_url="https://wikirate.org",
            required_env_keys=("WIKIRATE_TOKEN",),
        )

    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:  # noqa: D401
        env = self._get_env()
        metric = quote_plus(ctx["metric"])
        params = {"filter[industry]": ctx["industry"], "api_key": env["WIKIRATE_TOKEN"]}
        if ctx.get("year"):
            params["filter[year]"] = str(ctx["year"])
        if ctx.get("country"):
            params["filter[country]"] = ctx["country"]
        query = urlencode(params)
        url = f"{self.base_url}/{metric}.json" + (f"?{query}" if query else "")
        data = self._request_json(url)
        if isinstance(data, list):
            data = {"data": data}
        data["__metric"] = ctx["metric"]
        return data

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D401
        items = []
        metric = raw.get("__metric")
        for row in raw.get("data", []):
            items.append(
                {
                    "metric": metric,
                    "company": row.get("company") or row.get("company_name"),
                    "year": row.get("year"),
                    "value": row.get("value") or row.get("answer"),
                    "meta": row,
                }
            )
        return {"items": items}


__all__ = ["ESGReportsSectorWikiRate"]
