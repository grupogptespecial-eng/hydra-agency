import json
from pathlib import Path

SCHEMAS = [
    "dataset.schema.json",
    "backtest_report.schema.json",
    "ingest_lineage.schema.json",
    "dq_report.schema.json",
    "xbrl_output.schema.json",
]


def test_schemas_load() -> None:
    base = Path("packages/contracts/jsonschemas")
    for name in SCHEMAS:
        data = json.loads((base / name).read_text())
        assert "title" in data
