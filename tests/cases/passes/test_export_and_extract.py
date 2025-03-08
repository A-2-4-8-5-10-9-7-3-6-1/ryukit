import json
import pathlib
import subprocess
import tarfile
import tempfile
import typing

import jsonschema

from ...schemas.export_file import ENTITIES_ARRAY_SCHEMA
from ...utils.context_control import destroy_context
from ...utils.subprocesses import noE_execute

__all__ = []


def test_export_and_extract() -> None:
    """
    Test the export and extract commands.
    """

    size = 3

    [subprocess.run(["ryujinxkit", "save", "create"]) for _ in range(size)]

    with tempfile.TemporaryDirectory() as temp:
        path = pathlib.Path(temp) / "test.tar"

        noE_execute("ryujinxkit", "save", "export", "--output", str(path))

        with (
            tarfile.open(path) as tar,
            typing.cast(
                tarfile.ExFileObject, tar.extractfile("entities.json")
            ) as entities,
        ):
            entities_array = json.load(entities)

            assert len(entities_array) == size

            try:
                jsonschema.Draft202012Validator(
                    ENTITIES_ARRAY_SCHEMA
                ).validate(  # type: ignore
                    entities_array
                )

            except jsonschema.ValidationError:
                assert False

        destroy_context()

        assert (
            json.loads(
                noE_execute("ryujinxkit", "save", "extract", str(path)).stdout
            )["accepted"]
            == size
        )
