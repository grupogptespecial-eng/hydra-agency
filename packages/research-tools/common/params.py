"""Parser de parâmetros de data range e slicing."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DateRange:
    start: str
    end: str


def parse_params(params: dict) -> dict:
    """Normaliza parâmetros de busca em uma estrutura comum."""
    ranges = [DateRange(**r).__dict__ for r in params.get("date_ranges", [])]
    return {
        "date_ranges": ranges,
        "slicing_strategy": params.get("slicing_strategy", "fixed-window"),
    }
