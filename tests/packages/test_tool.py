import pathlib
import sys

# add repository root to PYTHONPATH
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from packages.tools import Tool, ToolResult


class DummyTool(Tool):
    def __init__(self):
        super().__init__(
            name="Dummy",
            category="test",
            scope="none",
            inputs_schema={"value"},
            output_schema="dummy_result",
            providers=["dummy"],
            ttl=0,
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
        )

    def call_providers(self, ctx, chunk=None):
        return {"value": ctx["value"]}

    def normalize(self, raw):
        return {"result": raw["value"]}

    def snapshot(self, data, meta):
        # return fake manifest
        return {"paths": ["/tmp/fake.json"], "checksum": "deadbeef"}


def test_tool_execute_basic():
    tool = DummyTool()
    result = tool.execute({"value": 1}, run_id="run1", agent_id="tester")

    assert isinstance(result, ToolResult)
    assert result.kind == "dummy_result"
    assert result.data == {"result": 1}
    assert result.meta["run_id"] == "run1"
    assert result.errors == []


def test_tool_cache_usage():
    tool = DummyTool()
    tool.ttl = "12h"
    tool._ttl_seconds = 12 * 3600
    ctx = {"value": 2}

    first = tool.execute(ctx, run_id="run1", agent_id="tester")
    second = tool.execute(ctx, run_id="run2", agent_id="tester")

    # second call should come from cache, keeping original run_id in meta
    assert second.meta["run_id"] == "run1"
    assert first.data == second.data
