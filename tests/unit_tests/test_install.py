import subprocess


def test() -> None:
    """
    Test the install command.
    """

    result = subprocess.run(
        args=["ryujinxkit", "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
