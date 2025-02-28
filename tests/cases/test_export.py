import json
import pathlib
import subprocess
import tarfile
import tempfile
import typing

import jsonschema

from ..schemas.export_file import ENTITIES_ARRAY_SCHEMA
from ..utils.noE_execute import noE_execute


def test_export() -> None:
    """
    Test the export command.
    """

    size = 10

    [subprocess.run(["ryujinxkit", "save", "create"]) for _ in range(size)]

    with tempfile.TemporaryDirectory() as temp:
        path = pathlib.Path(temp) / "test.tar"

        noE_execute("ryujinxkit", "save", "export", "--output", str(path))

        with (
            tarfile.open(path) as tar,
            typing.cast(
                tarfile.ExFileObject,
                tar.extractfile("entities.json"),
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
