from ryujinxkit.general import Session
from ryujinxkit.parser import parse

# =============================================================================


def main() -> None:
    """
    Entry point.
    """

    try:
        with Session:
            parse()

    except BaseException:
        pass


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# =============================================================================
