import pathlib
import importlib.util
import sys

# Add repo root to path for other package imports if necessary
repo_root = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(repo_root))

# Load ResearchTool dynamically because directory has a hyphen
module_path = repo_root / "packages" / "research-tools" / "base.py"
spec = importlib.util.spec_from_file_location("research_tools.base", module_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)  # type: ignore
ResearchTool = module.ResearchTool  # type: ignore


class DummyResearch(ResearchTool):
    def __init__(self):
        super().__init__(
            name="dummy",
            category="search",
            scope="world",
            inputs_schema=[],
            output_schema="research_bundle",
            providers=[lambda ctx, chunk: {"hello": "world"}],
            ttl=0,
            side_effects={"reads": [], "writes": []},
            allowed_agents={"tester"},
        )

    def normalize(self, raw):
        return raw


def test_execute_basic():
    tool = DummyResearch()
    result = tool.execute({}, run_id="1", agent_id="tester")
    assert result.data == {"hello": "world"}


def test_span_years():
    assert ResearchTool.span_years(2020, 2022) == "2020:2022"
    import pytest

    with pytest.raises(ValueError):
        ResearchTool.span_years(2022, 2020)
