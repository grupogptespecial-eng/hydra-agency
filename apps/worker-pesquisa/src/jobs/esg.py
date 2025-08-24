"""Job ESG"""
from packages.research_tools.common.params import parse_params  # type: ignore


def run(params: dict) -> dict:
    parsed = parse_params(params)
    return {"status": "ok", **parsed}
