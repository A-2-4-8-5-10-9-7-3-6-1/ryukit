import importlib.metadata
import json
import subprocess


def test() -> None:
    """
    Test the author command.
    """

    result = subprocess.run(
        args=["ryujinxkit", "--json", "--author"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert (
        json.loads(s=result.stdout)["author"]
        == importlib.metadata.metadata(distribution_name="ryujinxkit")[
            "Author"
        ]
    )
