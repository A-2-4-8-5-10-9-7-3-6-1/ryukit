import shutil

import pytest

from ryujinxkit.core.fs.node import Node
from ryujinxkit.core.fs.resolver import resolver


@pytest.fixture(autouse=True)
def destroy_context():
    """
    Destroy file-system context from previous tests.
    """

    [
        (
            shutil.rmtree(path=resolver[node], ignore_errors=True)
            if resolver[node].is_dir()
            else resolver[node].unlink(missing_ok=True)
        )
        for node in [
            Node.RYUJINXKIT_ROAMING_DATA,
            Node.RYUJINX_ROAMING_DATA,
            Node.RYUJINXKIT_SAVE_FOLDER,
        ]
    ]

    yield
