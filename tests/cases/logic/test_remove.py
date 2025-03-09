import json
import typing

import ryujinxkit.core.db.connection

from ...utils.subprocesses import NE_execute


def test_remove() -> None:
    """
    Test save-remove command.
    """

    NE_execute(
        "ryujinxkit",
        "save",
        "remove",
        str(
            json.loads(
                NE_execute("ryujinxkit", "--json", "save", "create").stdout
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
