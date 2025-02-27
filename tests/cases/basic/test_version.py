import importlib.metadata
import json

from ...utils.execute import execute


def test() -> None:
    """
    Test the version command.
    """

    assert json.loads(execute("ryujinxkit", "--json", "--version").stdout)[
        "version"
    ] == importlib.metadata.version("ryujinxkit")
