from ryujinxkit.general import Session
from ryujinxkit.parser import parse

# =============================================================================


def main() -> None:
    """
    Entry point.
    """

    with Session:
        parse()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# =============================================================================
