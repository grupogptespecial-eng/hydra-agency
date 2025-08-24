"""Helpers de defasagens e rolamentos."""
from typing import Iterable, List


def lag(series: List[float], k: int) -> List[float]:
    """Aplica defasagem simples preenchendo com 0."""
    return [0.0]*k + series[:-k] if k < len(series) else [0.0]*len(series)


def rolling_mean(series: List[float], window: int) -> List[float]:
    """Média móvel simples."""
    out: List[float] = []
    for i in range(len(series)):
        start = max(0, i-window+1)
        out.append(sum(series[start:i+1])/ (i-start+1))
    return out
