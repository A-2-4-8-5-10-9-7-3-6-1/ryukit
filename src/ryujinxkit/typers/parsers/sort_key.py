import re


def parser(key: str) -> tuple[str, str]:
    """
    Map a string to a column-direction pair.

    :param key: Key to map.

    :returns: Provided key as column-direction pair.

    :raises: `ValueError` If provided key is invalid.
    """

    key_pattern = "^(id|created|tag|updated|used|size)[+-]$"

    if re.match(string=key, pattern=key_pattern) is None:
        raise ValueError

    return (key[:-1], "asc" if key[-1] == "+" else "desc")
