"""Worker de backtesting de carteiras."""
from .compare import compare_portfolios


def main() -> None:
    compare_portfolios({}, {})


if __name__ == "__main__":
    main()
