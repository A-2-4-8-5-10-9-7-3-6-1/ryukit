import importlib.metadata
import json

from ...utils.execute import execute


def test_author() -> None:
    """
    Test the author command.
    """

    assert (
        json.loads(execute("ryujinxkit", "--json", "--author").stdout)[
            "author"
        ]
        == importlib.metadata.metadata("ryujinxkit")["author"]
    )
