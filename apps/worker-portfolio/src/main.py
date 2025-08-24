"""Worker de montagem de carteira."""
from packages.py_utils import storage, db  # type: ignore
from .optimize import optimize
from .adjust_sentiment import adjust


def main() -> None:
    dados = {"TICKER": 1.0}
    draft = optimize(dados)
    storage.save_artifact("portfolio_draft.json")
    final = adjust(draft)
    storage.save_artifact("portfolio_final.json")
    db.publish_artifact_event("run-demo", "BACKTEST_PENDING")


if __name__ == "__main__":
    main()
