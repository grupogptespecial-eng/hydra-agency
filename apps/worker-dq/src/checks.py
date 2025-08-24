"""Verificações simples de qualidade de dados."""
from typing import Iterable


def run_checks(rows: Iterable) -> dict:
    """Retorna relatório fictício de data quality."""
    return {"checked": len(list(rows))}
