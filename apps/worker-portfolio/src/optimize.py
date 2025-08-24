"""Rotinas de otimização de carteira base."""
from typing import Dict


def optimize(data: Dict) -> Dict:
    """Retorna rascunho de carteira com métricas fictícias."""
    weights = {k: 1/len(data) for k in data} if data else {}
    return {"weights": weights, "metrics": {"vol": 0.0}}
