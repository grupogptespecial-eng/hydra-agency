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
    module.__package__ = "packages.research-tools.datasets"
    spec.loader.exec_module(module)  # type: ignore
    return getattr(module, class_name)


DatasetsWorldWorldBank = load_class("packages/research-tools/datasets/world.py", "DatasetsWorldWorldBank")
DatasetsSectorFRED = load_class("packages/research-tools/datasets/sector.py", "DatasetsSectorFRED")
DatasetsCompanyAlphaVantage = load_class("packages/research-tools/datasets/company.py", "DatasetsCompanyAlphaVantage")


def test_world_worldbank(monkeypatch):
    tool = DatasetsWorldWorldBank()

    def fake_request(url: str, headers=None):
        return [
            {"page": 1},
            [
                {
                    "country": {"id": "BR"},
                    "indicator": {"id": "GDP"},
                    "date": "2020",
                    "value": 1.0,
                    "unit": "USD",
                }
            ],
        ]

    monkeypatch.setattr(tool, "_request_json", fake_request)
    res = tool.execute({"country_code": "BR", "series": "GDP"}, run_id="1", agent_id="tester")
    assert res.data["items"][0]["country"] == "BR"
    assert res.data["items"][0]["indicator"] == "GDP"


def test_sector_fred(monkeypatch):
    tool = DatasetsSectorFRED()

    def fake_env():
        return {"FRED_API_KEY": "x"}

    def fake_request(url: str, headers=None):
        return {
            "series_id": "DGS10",
            "units": "pc",
            "observations": [
                {"date": "2020-01-01", "value": "1.5"},
                {"date": "2020-01-02", "value": "."},
            ],
        }

    monkeypatch.setattr(tool, "_get_env", fake_env)
    monkeypatch.setattr(tool, "_request_json", fake_request)
    res = tool.execute({"series_id": "DGS10", "start_date": "2020-01-01", "end_date": "2020-01-02"}, run_id="1", agent_id="tester")
    assert res.data["items"][0]["value"] == pytest.approx(1.5)
    assert res.data["items"][1]["value"] is None


def test_company_alphavantage(monkeypatch):
    tool = DatasetsCompanyAlphaVantage()

    def fake_env():
        return {"ALPHAVANTAGE_KEY": "k"}

    def fake_request(url: str, headers=None):
        return {
            "Meta Data": {"2. Symbol": "AAPL"},
            "Time Series (Daily)": {
                "2020-01-01": {
                    "1. open": "1",
                    "2. high": "2",
                    "3. low": "0.5",
                    "4. close": "1.5",
                    "6. volume": "100",
                }
            },
        }

    monkeypatch.setattr(tool, "_get_env", fake_env)
    monkeypatch.setattr(tool, "_request_json", fake_request)
    res = tool.execute({"symbol": "AAPL"}, run_id="1", agent_id="tester")
    assert res.data["items"][0]["symbol"] == "AAPL"
    assert res.data["items"][0]["close"] == pytest.approx(1.5)
