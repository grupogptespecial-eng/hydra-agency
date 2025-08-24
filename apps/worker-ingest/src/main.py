"""Worker de ingestão genérica."""
from .ingest import ingest_source


def main() -> None:
    ingest_source("example")


if __name__ == "__main__":
    main()
