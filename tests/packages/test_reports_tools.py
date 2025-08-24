import importlib.util
import pathlib
import sys

import pytest

repo_root = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(repo_root))


def load_class(module_relative_path: str, class_name: str):
    module_path = repo_root / module_relative_path
    spec = importlib.util.spec_from_file_location(class_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    module.__package__ = "packages.research-tools.reports"
    spec.loader.exec_module(module)  # type: ignore
    return getattr(module, class_name)


general_world = load_class(
    "packages/research-tools/reports/world.py", "GeneralReportsWorldWDS"
)
general_sector = load_class(
    "packages/research-tools/reports/sector.py", "GeneralReportsSectorSECEdgar"
)
general_company = load_class(
    "packages/research-tools/reports/company.py", "GeneralReportsCompanyCVMDadosAbertos"
)


def test_world_wds(monkeypatch):
    tool = general_world()

    def fake_request(url: str, headers=None):
        return {
            "documents": [
                {
                    "display_title": "World Dev Report",
                    "disclosure_year": 2024,
                    "pdfurl": "http://wds.pdf",
                    "region": "Global",
                    "topics": ["Economy"],
                }
            ]
        }

    monkeypatch.setattr(tool, "_request_json", fake_request)
    res = tool.execute({"start_year": 2023, "end_year": 2024}, run_id="1", agent_id="tester")
    assert res.data["items"][0]["title"] == "World Dev Report"


def test_sector_sec(monkeypatch):
    tool = general_sector()

    def fake_get_env():
        return {"SEC_EDGAR_API": "{\"User-Agent\": \"x\", \"Accept-Encoding\": \"gzip, deflate\", \"Host\": \"data.sec.gov\"}"}

    monkeypatch.setattr(tool, "_get_env", fake_get_env)

    def fake_request(url: str, headers=None):
        assert headers == {
            "User-Agent": "x",
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov",
        }
        return {
            "filings": {
                "recent": {
                    "accessionNumber": ["0001"],
                    "form": ["10-K"],
                    "filingDate": ["2024-01-01"],
                }
            }
        }

    monkeypatch.setattr(tool, "_request_json", fake_request)
    res = tool.execute({"cik": "1234"}, run_id="1", agent_id="tester")
    assert res.data["items"][0]["form"] == "10-K"


def test_company_cvm(monkeypatch):
    tool = general_company()

    def fake_bytes(url: str, headers=None):
        return b"col1,col2\n1,2\n"

    monkeypatch.setattr(tool, "_request_bytes", fake_bytes)
    res = tool.execute({"path": "/dados/foo.csv"}, run_id="1", agent_id="tester")
    assert res.data["items"][0]["col1"] == "1"
