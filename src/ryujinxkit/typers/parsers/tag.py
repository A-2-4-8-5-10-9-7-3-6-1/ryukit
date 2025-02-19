def parser(tag: str) -> str:
    """
    Validate tags.

    :param tag: Tag to be validated.

    :returns: The formatted tag.

    :raises: `ValueError` if the tag is invalid.
    """

    tag = tag.strip()

    if tag == "" or not tag[0].isalnum() or " " in tag:
        raise ValueError

    return tag
