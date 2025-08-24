"""Funções utilitárias para gerar lags e janelas rolantes."""
from typing import Iterable


def build_features(prices: Iterable[float]) -> dict:
    """Gera features simples e retorna um manifest fictício."""
    # Implementação real lidará com lags, rolling e as_of
    return {"rows": len(list(prices))}
