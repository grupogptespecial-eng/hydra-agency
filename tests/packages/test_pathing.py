import importlib.util
import pathlib
import sys

repo_root = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(repo_root))

module_path = repo_root / "packages" / "research-tools" / "common" / "pathing.py"
spec = importlib.util.spec_from_file_location("research_tools.common.pathing", module_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)  # type: ignore
build_key = module.build_key  # type: ignore


def test_build_key_basic():
    assert build_key("ESGReport", "Company", "123") == "ESGReport/Company/123"


def test_build_key_sanitizes():
    assert build_key(" Report ", "Sector", "A/B") == "Report/Sector/A-B"
