from __future__ import annotations

from typing import Any, Dict, Optional
import xml.etree.ElementTree as ET
import importlib.util
from pathlib import Path

_base_spec = importlib.util.spec_from_file_location(
    "research_tools.base", Path(__file__).resolve().parents[1] / "base.py"
)
_base_module = importlib.util.module_from_spec(_base_spec)
assert _base_spec.loader is not None  # pragma: no cover
_base_spec.loader.exec_module(_base_module)  # type: ignore
ResearchTool = _base_module.ResearchTool  # type: ignore


class NewsCompanyRSS(ResearchTool):
    """Fetch company news from an RSS/Atom feed."""

    def __init__(self) -> None:
        super().__init__(
            name="NewsCompanyRSS",
            category="search",
            scope="company",
            inputs_schema={"feed_url", "min_date_iso?"},
            output_schema="research_bundle",
            providers=[],
            ttl="12h",
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
        )

    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:  # noqa: D401
        content = self._request_bytes(ctx["feed_url"])
        return {"xml": content, "min_date_iso": ctx.get("min_date_iso")}

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D401
        xml_bytes = raw.get("xml", b"")
        min_iso = raw.get("min_date_iso")
        root = ET.fromstring(xml_bytes)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = []
        for entry in root.findall(".//atom:entry", ns):
            link = entry.find("atom:link", ns)
            updated = entry.findtext("atom:updated", "", ns)
            if min_iso and updated < min_iso:
                continue
            items.append(
                {
                    "title": (entry.findtext("atom:title", "", ns) or "").strip(),
                    "url": link.attrib.get("href") if link is not None else "",
                    "updated": updated,
                }
            )
        for item in root.findall(".//item"):
            pub = item.findtext("pubDate", "")
            if min_iso and pub < min_iso:
                continue
            items.append(
                {
                    "title": (item.findtext("title") or "").strip(),
                    "url": item.findtext("link") or "",
                    "pubDate": pub,
                }
            )
        return {"items": items}


__all__ = ["NewsCompanyRSS"]
