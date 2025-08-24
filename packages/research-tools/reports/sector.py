from __future__ import annotations

from typing import Any, Dict, Optional, List
import json
import importlib.util
from pathlib import Path

_base_spec = importlib.util.spec_from_file_location(
    "research_tools.base", Path(__file__).resolve().parents[1] / "base.py"
)
_base_module = importlib.util.module_from_spec(_base_spec)
assert _base_spec.loader is not None  # pragma: no cover
_base_spec.loader.exec_module(_base_module)  # type: ignore
ResearchTool = _base_module.ResearchTool  # type: ignore


class GeneralReportsSectorSECEdgar(ResearchTool):
    """Fetch recent filings from the SEC EDGAR API for a given CIK."""

    def __init__(self) -> None:
        super().__init__(
            name="GeneralReportsSectorSECEdgar",
            category="search",
            scope="sector",
            inputs_schema={"cik"},
            output_schema="research_bundle",
            providers=[],
            ttl="7d",
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
            base_url="https://data.sec.gov/submissions/",
            required_env_keys=("SEC_EDGAR_API",),
        )

    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        env = self._get_env()
        headers: Dict[str, str] = {}
        raw_hdrs = env.get("SEC_EDGAR_API")
        if raw_hdrs:
            try:
                headers = json.loads(raw_hdrs)
            except Exception:
                headers = {"User-Agent": raw_hdrs}
        cik = str(ctx["cik"]).zfill(10)
        url = f"{self.base_url}CIK{cik}.json"
        return self._request_json(url, headers=headers)

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        filings = raw.get("filings", {}).get("recent", {})
        acc = filings.get("accessionNumber", [])
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        items: List[Dict[str, Any]] = []
        for accession, form, date in zip(acc, forms, dates):
            items.append({"accession": accession, "form": form, "filing_date": date})
        return {"items": items}


__all__ = ["GeneralReportsSectorSECEdgar"]
