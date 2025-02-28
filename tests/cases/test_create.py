import collections.abc
import subprocess

import pytest


@pytest.mark.parametrize(
    argnames="args,valid",
    argvalues=[
        ([], True),
        (["--tag", "first"], True),
        (["--tag", ""], False),
        (["--tag", "split text"], False),
        (["--tag", "special-character*"], True),
        (["--tag", "1"], True),
    ],
)
def test_create(args: collections.abc.Sequence[str], valid: bool) -> None:
    """
    Test the save-create command.

    :param args: Additional args to pass into call.
    :param valid: Whether or not the call is expected to succeed.
    """

    assert (
        subprocess.run(
            ["ryujinxkit", "--json", "save", "create", *args]
        ).returncode
        == 0
    ) == valid
