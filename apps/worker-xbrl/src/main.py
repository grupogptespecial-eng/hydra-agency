"""Worker de parsing XBRL."""
from .parse_xbrl import parse_document


def main() -> None:
    parse_document("example.xbrl")


if __name__ == "__main__":
    main()
