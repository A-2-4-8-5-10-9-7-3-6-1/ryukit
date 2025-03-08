import json
import typing

import ryujinxkit.core.db.connection

from ...utils.subprocesses import noE_execute

__all__ = []


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

    with ryujinxkit.core.db.connection.connect() as connection:

        class QueryRow(typing.TypedDict):
            count: int

        assert (
            typing.cast(
                QueryRow,
                connection.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM saves
                    """
                ).fetchone(),
            )["count"]
            == 0
        )
