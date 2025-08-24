from __future__ import annotations

import importlib.util
import io
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from packages.tools.base import ToolResult

ROOT = Path(__file__).resolve().parents[4]


def _load_tool(rel_path: str, class_name: str):
    spec = importlib.util.spec_from_file_location(class_name, ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    module.__package__ = "packages.research-tools"
    spec.loader.exec_module(module)  # type: ignore
    return getattr(module, class_name)

TOOL_MAP = {
    "datasets": {
        "DatasetsWorldWorldBank": _load_tool("packages/research-tools/datasets/world.py", "DatasetsWorldWorldBank"),
        "DatasetsSectorFRED": _load_tool("packages/research-tools/datasets/sector.py", "DatasetsSectorFRED"),
        "DatasetsCompanyAlphaVantage": _load_tool(
            "packages/research-tools/datasets/company.py", "DatasetsCompanyAlphaVantage"
        ),
    },
    "esg": {
        "ESGReportsWorldUNSDG": _load_tool("packages/research-tools/esg/world.py", "ESGReportsWorldUNSDG"),
        "ESGReportsSectorWikiRate": _load_tool("packages/research-tools/esg/sector.py", "ESGReportsSectorWikiRate"),
        "ESGReportsCompanyWikiRate": _load_tool("packages/research-tools/esg/company.py", "ESGReportsCompanyWikiRate"),
    },
    "news": {
        "NewsWorldGDELT": _load_tool("packages/research-tools/news/world.py", "NewsWorldGDELT"),
        "NewsSectorRSS": _load_tool("packages/research-tools/news/sector.py", "NewsSectorRSS"),
        "NewsCompanyRSS": _load_tool("packages/research-tools/news/company.py", "NewsCompanyRSS"),
    },
    "reports": {
        "GeneralReportsWorldWDS": _load_tool("packages/research-tools/reports/world.py", "GeneralReportsWorldWDS"),
        "GeneralReportsSECEdgar": _load_tool("packages/research-tools/reports/sector.py", "GeneralReportsSectorSECEdgar"),
        "GeneralReportsCVMDadosAbertos": _load_tool(
            "packages/research-tools/reports/company.py", "GeneralReportsCompanyCVMDadosAbertos"
        ),
    },
}

router = APIRouter(prefix="/debug")


def _get_tool(tool_type: str, tool_name: str):
    tools = TOOL_MAP.get(tool_type)
    if not tools:
        raise HTTPException(status_code=404, detail="unknown tool type")
    cls = tools.get(tool_name)
    if cls is None:
        raise HTTPException(status_code=404, detail="unknown tool")
    return cls()


@router.post("/tool/{tool_type}/{tool_name}")
async def run_tool(tool_type: str, tool_name: str, request: Request) -> Any:
    """Execute a research tool for debugging purposes."""
    tool = _get_tool(tool_type, tool_name)

    ctype = request.headers.get("content-type", "")
    if ctype.startswith("multipart/form-data"):
        form = await request.form()
        kwargs: Dict[str, Any] = {}
        for k, v in form.items():
            if isinstance(v, UploadFile):
                kwargs[k] = await v.read()
            else:
                kwargs[k] = v
    elif ctype.startswith("application/json"):
        kwargs = await request.json()
    else:
        kwargs = {}

    result: ToolResult = tool.execute(kwargs, run_id="debug", agent_id="tester")
    data = result.data

    if isinstance(data, dict) and "raw_bytes" in data:
        filename = data.get("filename", "output.bin")
        return StreamingResponse(
            io.BytesIO(data["raw_bytes"]),
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            media_type="application/octet-stream",
        )

    return JSONResponse(data)
