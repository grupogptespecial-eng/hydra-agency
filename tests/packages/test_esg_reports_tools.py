import importlib.util
import pathlib
import sys

import pytest

# Resolve repository root and extend sys.path
repo_root = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(repo_root))

# Helper to dynamically load module

def load_class(module_relative_path: str, class_name: str):
    module_path = repo_root / module_relative_path
    spec = importlib.util.spec_from_file_location(class_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    module.__package__ = "packages.research-tools.esg"
    spec.loader.exec_module(module)  # type: ignore
    return getattr(module, class_name)


ESGReportsWorldUNSDG = load_class("packages/research-tools/esg/world.py", "ESGReportsWorldUNSDG")
ESGReportsSectorWikiRate = load_class("packages/research-tools/esg/sector.py", "ESGReportsSectorWikiRate")
ESGReportsCompanyWikiRate = load_class("packages/research-tools/esg/company.py", "ESGReportsCompanyWikiRate")


def test_world_unsdg(monkeypatch):
    tool = ESGReportsWorldUNSDG()

    def fake_request(url: str, headers=None):
        return {
            "data": [
                {
                    "geoAreaCode": "BRA",
                    "timePeriod": "2020",
                    "value": "1.2",
                    "attributes": {"unit": "pct"},
                }
            ],
            "seriesCode": "SG_DUR_TOTL",
        }

    monkeypatch.setattr(tool, "_request_json", fake_request)
    res = tool.execute({"series_code": "SG_DUR_TOTL"}, run_id="1", agent_id="tester")
    assert res.data["items"][0]["country"] == "BRA"
    assert res.data["items"][0]["value"] == pytest.approx(1.2)


def test_sector_wikirate(monkeypatch):
    tool = ESGReportsSectorWikiRate()

    def fake_request(url: str, headers=None):
        assert "api_key=token" in url
        return [
            {"company": "ACME", "year": 2021, "value": "5"},
            {"company_name": "OTHER", "year": 2020, "answer": "3"},
        ]

    monkeypatch.setenv("WIKIRATE_TOKEN", "token")
    monkeypatch.setattr(tool, "_request_json", fake_request)
    res = tool.execute({"metric": "Carbon", "industry": "Tech"}, run_id="1", agent_id="tester")
    assert len(res.data["items"]) == 2
    assert res.data["items"][0]["metric"] == "Carbon"


def test_company_wikirate(monkeypatch):
    tool = ESGReportsCompanyWikiRate()

    def fake_request(url: str, headers=None):
        assert "api_key=token" in url
        return [{"company": "ACME", "year": 2021, "value": "5"}]

    monkeypatch.setenv("WIKIRATE_TOKEN", "token")
    monkeypatch.setattr(tool, "_request_json", fake_request)
    res = tool.execute({"metric": "Carbon", "company_name": "ACME"}, run_id="1", agent_id="tester")
    assert res.data["items"][0]["company"] == "ACME"
    assert res.data["items"][0]["metric"] == "Carbon"
