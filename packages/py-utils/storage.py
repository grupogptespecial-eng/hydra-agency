"""Funções utilitárias de armazenamento."""
from pathlib import Path
from typing import Union


def save_artifact(path: Union[str, Path]) -> str:
    """Finge salvar um artefato e retorna seu ID."""
    return str(path)


def get_presigned_url(path: Union[str, Path]) -> str:
    """Retorna uma URL fictícia assinada para download."""
    return f"https://example.com/{path}"


def fetch_artifact(path: Union[str, Path]) -> bytes:
    """Lê um artefato e retorna bytes (placeholder)."""
    return b""
