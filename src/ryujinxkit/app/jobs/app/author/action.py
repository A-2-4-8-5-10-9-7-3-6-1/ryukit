import importlib.metadata


def action() -> str:
    """
    Get app's author.

    :returns: App's author.
    """

    return importlib.metadata.metadata("ryujinxkit")["author"]
