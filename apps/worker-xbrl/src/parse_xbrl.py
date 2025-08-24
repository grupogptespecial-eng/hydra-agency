"""Parser mínimo de XBRL."""

def parse_document(path: str) -> dict:
    """Retorna estrutura fictícia a partir de um documento XBRL."""
    return {"path": path, "facts": 0}
