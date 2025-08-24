from fastapi.testclient import TestClient

import importlib.util
from pathlib import Path
import sys
from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

spec = importlib.util.spec_from_file_location(
    "debug_router", Path(__file__).resolve().parents[2] / "apps" / "api" / "app" / "routers" / "debug.py"
)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)  # type: ignore

app = FastAPI()
app.include_router(module.router)

from packages.tools.base import ToolResult


def test_debug_tool_json(monkeypatch):
    def fake_exec(self, ctx, run_id, agent_id):
        return ToolResult(kind="dataset", data={"echo": ctx}, meta={}, errors=[])

    tool_cls = module.TOOL_MAP["datasets"]["DatasetsWorldWorldBank"]
    monkeypatch.setattr(tool_cls, "execute", fake_exec)
    client = TestClient(app)
    payload = {"country_code": "BR", "series": "GDP", "start_year": 2000, "end_year": 2001}
    resp = client.post("/debug/tool/datasets/DatasetsWorldWorldBank", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"echo": payload}


def test_debug_tool_file(monkeypatch):
    def fake_exec(self, ctx, run_id, agent_id):
        return ToolResult(
            kind="dataset",
            data={"raw_bytes": b"hi", "filename": "out.txt"},
            meta={},
            errors=[],
        )

    tool_cls = module.TOOL_MAP["datasets"]["DatasetsWorldWorldBank"]
    monkeypatch.setattr(tool_cls, "execute", fake_exec)
    client = TestClient(app)
    resp = client.post(
        "/debug/tool/datasets/DatasetsWorldWorldBank",
        files={"dummy": ("dummy.txt", b"content")},
    )
    assert resp.status_code == 200
    assert resp.content == b"hi"
    assert resp.headers["content-disposition"].startswith("attachment; filename=\"out.txt\"")
