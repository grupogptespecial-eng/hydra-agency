"""Worker de checagem de dados."""
from .checks import run_checks


def main() -> None:
    run_checks([])


if __name__ == "__main__":
    main()
