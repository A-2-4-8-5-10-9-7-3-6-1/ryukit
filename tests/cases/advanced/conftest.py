import shutil
import subprocess

import pytest

from ryujinxkit.core.fs.node import Node
from ryujinxkit.core.fs.resolver import resolver


@pytest.fixture(scope="package")
def setup_database():
    [subprocess.run(args=["ryujinxkit", "save", "create"]) for _ in range(100)]

    yield "Testing with 100 save instances."

    [
        shutil.rmtree(path=resolver[node], ignore_errors=True)
        for node in [
            Node.RYUJINXKIT_ROAMING_DATA,
            Node.RYUJINX_ROAMING_DATA,
            Node.RYUJINXKIT_SAVE_FOLDER,
        ]
    ]
