"""Funções de ingestão com registro de lineage."""

def ingest_source(name: str) -> dict:
    """Realiza ingestão fictícia e retorna metadados."""
    return {"source": name, "rows": 0}
