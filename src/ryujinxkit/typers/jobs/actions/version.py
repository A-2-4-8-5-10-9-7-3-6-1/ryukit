import importlib.metadata


def action() -> str:
    """
    Get app's version.

    :returns: App's version.
    """

    return importlib.metadata.version(distribution_name="ryujinxkit")
