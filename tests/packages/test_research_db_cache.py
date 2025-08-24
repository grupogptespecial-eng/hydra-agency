import importlib.util
import pathlib
import sys

import pytest

repo_root = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(repo_root))

# Load modules dynamically due to hyphen in folder name
base_path = repo_root / "packages" / "research-tools" / "base.py"
base_spec = importlib.util.spec_from_file_location("research_tools.base", base_path)
base_module = importlib.util.module_from_spec(base_spec)
assert base_spec.loader is not None
base_spec.loader.exec_module(base_module)  # type: ignore
ResearchTool = base_module.ResearchTool  # type: ignore

# Use the same in-memory DB instance as ResearchTool
db = base_module.db  # type: ignore[attr-defined]


class DummyTool(ResearchTool):
    def __init__(self):
        self.calls = 0
        super().__init__(
            name="dummy",
            category="search",
            scope="company",
            inputs_schema={"code"},
            output_schema="dataset",
            providers=[self._provider],
            ttl=0,
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
        )

    def _provider(self, ctx, chunk):
        self.calls += 1
        return {"value": ctx["code"]}

    def normalize(self, raw):
        return raw


def setup_function(_):
    db.clear()


def test_db_caching():
    tool = DummyTool()
    ctx = {"code": "ABC", "data_type": "Test", "level": "Company"}

    r1 = tool.execute(ctx, run_id="1", agent_id="tester")
    assert r1.data == {"value": "ABC"}
    assert tool.calls == 1

    # Second call should hit DB cache, not provider
    r2 = tool.execute(ctx, run_id="2", agent_id="tester")
    assert r2.data == {"value": "ABC"}
    assert tool.calls == 1
    assert r2.meta.get("db_key") == "Test/Company/ABC"


def test_db_hit_skips_provider():
    """If data already exists in DB, provider is not called."""
    tool = DummyTool()
    ctx = {"code": "XYZ", "data_type": " Report ", "level": " Sector"}

    # Pre-seed DB with sanitized key
    db.save("Report/Sector/XYZ", {"value": "cached"})

    result = tool.execute(ctx, run_id="3", agent_id="tester")

    assert result.data == {"value": "cached"}
    assert tool.calls == 0
    assert result.meta.get("db_key") == "Report/Sector/XYZ"
