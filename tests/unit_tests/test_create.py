import subprocess
from typing import Sequence

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
def test(args: Sequence[str], valid: bool) -> None:
    """
    Test the save-create command.
    """

    result = subprocess.run(
        args=[],
        capture_output=True,
        text=True,
    )

    assert (result.returncode == 0) == valid
