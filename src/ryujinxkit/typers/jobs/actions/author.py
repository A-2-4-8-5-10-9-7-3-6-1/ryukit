import importlib.metadata


def action() -> str:
    """
    Get app's author.

    :returns: App's author.
    """

    return f"{
        importlib.metadata.metadata(distribution_name="ryujinxkit")["Author"]
    }"
