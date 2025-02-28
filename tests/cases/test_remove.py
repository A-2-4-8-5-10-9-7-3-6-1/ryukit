import json

from ..utils.noE_execute import noE_execute


def test_remove() -> None:
    """
    Test save-remove command.
    """

    noE_execute(
        "ryujinxkit",
        "save",
        "remove",
        str(
            json.loads(
                noE_execute("ryujinxkit", "--json", "save", "create").stdout
            )["id"]
        ),
    )
