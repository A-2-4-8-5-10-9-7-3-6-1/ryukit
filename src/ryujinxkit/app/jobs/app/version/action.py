import importlib.metadata


def action() -> str:
    """
    Get app's version.

    :returns: App's version.
    """

    return importlib.metadata.version("ryujinxkit")
