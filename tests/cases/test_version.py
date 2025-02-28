import importlib.metadata
import json

from ..utils.noE_execute import noE_execute


def test_version() -> None:
    """
    Test the version command.
    """

    assert json.loads(noE_execute("ryujinxkit", "--json", "--version").stdout)[
        "version"
    ] == importlib.metadata.version("ryujinxkit")
