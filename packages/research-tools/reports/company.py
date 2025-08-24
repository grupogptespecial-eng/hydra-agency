from __future__ import annotations

from typing import Any, Dict, Optional, List
import csv
import io
import importlib.util
from pathlib import Path

_base_spec = importlib.util.spec_from_file_location(
    "research_tools.base", Path(__file__).resolve().parents[1] / "base.py"
)
_base_module = importlib.util.module_from_spec(_base_spec)
assert _base_spec.loader is not None  # pragma: no cover
_base_spec.loader.exec_module(_base_module)  # type: ignore
ResearchTool = _base_module.ResearchTool  # type: ignore


class GeneralReportsCompanyCVMDadosAbertos(ResearchTool):
    """Fetch datasets from CVM Dados Abertos and convert CSVs to JSON."""

    def __init__(self) -> None:
        super().__init__(
            name="GeneralReportsCompanyCVMDadosAbertos",
            category="search",
            scope="company",
            inputs_schema={"path"},
            output_schema="research_bundle",
            providers=[],
            ttl="30d",
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
            base_url="https://dados.cvm.gov.br",
        )

    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> bytes:
        url = f"{self.base_url}{ctx['path']}"
        return self._request_bytes(url)

    def normalize(self, raw: bytes) -> Dict[str, Any]:
        try:
            text = raw.decode("utf-8", errors="replace")
            reader = csv.DictReader(io.StringIO(text))
            items: List[Dict[str, Any]] = list(reader)
            return {"items": items[:1000], "truncated": len(items) > 1000}
        except Exception:
            return {"raw_bytes": raw[:100]}


__all__ = ["GeneralReportsCompanyCVMDadosAbertos"]
