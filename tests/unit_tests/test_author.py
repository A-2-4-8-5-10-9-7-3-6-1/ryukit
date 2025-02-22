import importlib.metadata
import json
import subprocess

from ..decorators.execute import execute


@execute("ryujinxkit", "--json", "--author")
def test_author(results: subprocess.CompletedProcess[str]) -> None:
    """
    Test the author command.
    """

    assert (
        json.loads(s=results.stdout)["author"]
        == importlib.metadata.metadata("ryujinxkit")["author"]
    )
