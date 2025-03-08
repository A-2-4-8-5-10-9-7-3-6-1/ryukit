import shutil

import ryujinxkit.core.fs.resolver

__all__ = ["destroy_context"]


def destroy_context():
    """
    Destroy file-system context after previous tests.
    """

    [
        (
            shutil.rmtree(
                path=ryujinxkit.core.fs.resolver.resolver[node],
                ignore_errors=True,
            )
            if ryujinxkit.core.fs.resolver.resolver[node].is_dir()
            else ryujinxkit.core.fs.resolver.resolver[node].unlink(
                missing_ok=True
            )
        )
        for node in [
            ryujinxkit.core.fs.resolver.Node.RYUJINXKIT_ROAMING_DATA,
            ryujinxkit.core.fs.resolver.Node.RYUJINX_ROAMING_DATA,
            ryujinxkit.core.fs.resolver.Node.RYUJINXKIT_SAVE_FOLDER,
        ]
    ]
