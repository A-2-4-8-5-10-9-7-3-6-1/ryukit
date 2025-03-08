import json
import typing

import ryujinxkit.core.db.connection

from ...extras.ryujinxkit.models.command_jsons import SaveCreateCommandJSON
from ...utils.subprocesses import noE_execute

__all__ = []


def test_retag() -> None:
    """
    Test the retag command.
    """

    id_ = str(
        typing.cast(
            SaveCreateCommandJSON,
            json.loads(
                noE_execute("ryujinxkit", "--json", "save", "create").stdout
            ),
        )["id"]
    )

    noE_execute("ryujinxkit", "save", "retag", id_, "test-tag")

    with ryujinxkit.core.db.connection.connect() as connection:

        class QueryRow(typing.TypedDict):
            tag: str

        assert (
            typing.cast(
                QueryRow,
                connection.execute(
                    """
                    SELECT tag
                    FROM saves
                    WHERE id = :id;
                    """,
                    {"id": id_},
                ).fetchone(),
            )["tag"]
            == "test-tag"
        )
