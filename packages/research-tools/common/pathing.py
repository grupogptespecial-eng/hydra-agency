"""Helpers para construir chaves hierárquicas de pesquisa."""

def build_key(data_type: str, level: str, code: str) -> str:
    """Gera caminho ``tipo/nivel/codigo`` padronizado.

    A função remove espaços extras e evita barras adicionais, garantindo
    que o formato seja consistente para uso no banco de dados ou cache.
    """

    def _clean(part: str) -> str:
        return str(part).strip().replace("/", "-")

    return f"{_clean(data_type)}/{_clean(level)}/{_clean(code)}"


__all__ = ["build_key"]
