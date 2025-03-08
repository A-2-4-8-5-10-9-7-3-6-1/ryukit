import importlib.metadata
import json

from ...extras.ryujinxkit.models.command_jsons import (
    AuthorCommandJSON,
    VersionCommandJSON,
)
from ...utils.subprocesses import noE_execute

__all__ = []


def test_meta() -> None:
    """
    Test meta commands.
    """

    def author_check(jsn: AuthorCommandJSON) -> bool:
        return (
            jsn["author"]
            == importlib.metadata.metadata("ryujinxkit")["author"]
        )

    def version_check(jsn: VersionCommandJSON) -> bool:
        return jsn["version"] == importlib.metadata.version("ryujinxkit")

    for command, check in [
        (["--version"], version_check),
        (["--author"], author_check),
    ]:
        assert check(
            json.loads(noE_execute("ryujinxkit", "--json", *command).stdout)
        )
