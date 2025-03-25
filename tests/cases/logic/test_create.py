import collections.abc
import json
import typing

import pytest
import ryujinxkit.core.db.connection

from ...extras.ryujinxkit.models.command_jsons import SaveCreateCommandJSON
from ...utils.subprocesses import NE_execute


@pytest.mark.parametrize(
    argnames="args",
    argvalues=[
        [],
        ["--tag", "first"],
        ["--tag", "special-character*"],
        ["--tag", "1"],
    ],
)
def test_create(args: collections.abc.Sequence[str]) -> None:
    """
    Test the save-create command.

    :param args: Additional args to pass into call.
    """

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
                    WHERE id = :id;
                    """,
                    typing.cast(
                        SaveCreateCommandJSON,
                        json.loads(
                            NE_execute(
                                "ryujinxkit", "--json", "save", "create", *args
                            ).stdout
                        ),
                    ),
                ).fetchone(),
            )["count"]
            == 1
        )
