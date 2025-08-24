"""Aplica ajustes de sentimento na carteira."""
from typing import Dict


def adjust(draft: Dict) -> Dict:
    """Gera carteira final com justificativas fictícias."""
    return {
        "weights": draft.get("weights", {}),
        "justificativas": ["sentimento neutro"],
    }
