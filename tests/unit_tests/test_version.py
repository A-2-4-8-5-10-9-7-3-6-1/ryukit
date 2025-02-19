import importlib.metadata
import json
import subprocess


def test() -> None:
    """
    Test the version command.
    """

    result = subprocess.run(
        args=["ryujinxkit", "--json", "--version"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert json.loads(s=result.stdout)[
        "version"
    ] == importlib.metadata.version(distribution_name="ryujinxkit")
