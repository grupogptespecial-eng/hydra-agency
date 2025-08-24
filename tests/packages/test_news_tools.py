import importlib.util
import pathlib
import sys

import pytest

# Resolve repository root and extend sys.path
repo_root = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(repo_root))


def load_class(module_relative_path: str, class_name: str):
    module_path = repo_root / module_relative_path
    spec = importlib.util.spec_from_file_location(class_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    module.__package__ = "packages.research-tools.news"
    spec.loader.exec_module(module)  # type: ignore
    return getattr(module, class_name)


NewsWorldGDELT = load_class("packages/research-tools/news/world.py", "NewsWorldGDELT")
NewsSectorRSS = load_class("packages/research-tools/news/sector.py", "NewsSectorRSS")
NewsCompanyRSS = load_class("packages/research-tools/news/company.py", "NewsCompanyRSS")


def test_world_gdelt(monkeypatch):
    tool = NewsWorldGDELT()

    def fake_request(url: str, headers=None):
        return {
            "events": [
                {
                    "Day": "20240101",
                    "SOURCEURL": "http://ex.com",
                    "ActionGeo_CountryCode": "US",
                    "Themes": "ECON",
                    "Actor1Name": "A1",
                    "Actor2Name": "A2",
                    "AvgTone": "1.5",
                }
            ]
        }

    monkeypatch.setattr(tool, "_request_json", fake_request)
    res = tool.execute({"query": "test", "start_datetime": "20240101000000", "end_datetime": "20240102000000"}, run_id="1", agent_id="tester")
    assert res.data["items"][0]["country"] == "US"
    assert res.data["count"] == 1


def test_sector_rss(monkeypatch):
    tool = NewsSectorRSS()

    def fake_bytes(url: str, headers=None):
        return b"""
        <rss><channel>
            <item><title>Foo</title><link>http://foo</link><pubDate>2024-01-01</pubDate></item>
        </channel></rss>"""

    monkeypatch.setattr(tool, "_request_bytes", fake_bytes)
    res = tool.execute({"feed_url": "http://feed"}, run_id="1", agent_id="tester")
    assert res.data["items"][0]["title"] == "Foo"


def test_company_rss(monkeypatch):
    tool = NewsCompanyRSS()

    def fake_bytes(url: str, headers=None):
        return b"""
        <feed xmlns='http://www.w3.org/2005/Atom'>
            <entry><title>Bar</title><link href='http://bar'/><updated>2024-01-02</updated></entry>
        </feed>"""

    monkeypatch.setattr(tool, "_request_bytes", fake_bytes)
    res = tool.execute({"feed_url": "http://feed"}, run_id="1", agent_id="tester")
    assert res.data["items"][0]["title"] == "Bar"
