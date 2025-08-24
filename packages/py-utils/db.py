"""Funções utilitárias de banco de dados.

Este módulo fornece helpers mínimos para simular operações de
persistência. Para fins de testes e desenvolvimento local, os dados são
armazenados em um dicionário em memória. Em produção, esses helpers
deveriam ser substituídos por chamadas a um banco de dados real.
"""

from typing import Any, Dict, Optional

# armazenamento chave → valor simples em memória
_DB: Dict[str, Any] = {}


def fetch(path: str) -> Optional[Any]:
    """Obtém um registro salvo no caminho ``path``.

    Parameters
    ----------
    path: str
        Caminho hierárquico ``tipo/nivel/identificador``.
    """

    return _DB.get(path)


def save(path: str, data: Any) -> None:
    """Persiste ``data`` sob ``path``."""

    _DB[path] = data


def clear() -> None:
    """Limpa o armazenamento em memória (apenas para testes)."""

    _DB.clear()


def publish_artifact_event(run_id: str, artifact_id: str) -> None:
    """Emite evento fictício para um artefato salvo."""

    print(f"EVENT {run_id} {artifact_id}")


__all__ = ["fetch", "save", "clear", "publish_artifact_event"]
