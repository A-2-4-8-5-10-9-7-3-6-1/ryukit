import importlib.metadata
import json

from ..utils.noE_execute import noE_execute


def test_author() -> None:
    """
    Test the author command.
    """

    assert (
        json.loads(noE_execute("ryujinxkit", "--json", "--author").stdout)[
            "author"
        ]
        == importlib.metadata.metadata("ryujinxkit")["author"]
    )
