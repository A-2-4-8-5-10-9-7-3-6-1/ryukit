"""
- dependency level 1.
"""

from ..configs import DATABASE_SAVE_TAG_DEFAULT

# =============================================================================


def format_tag(tag: str) -> str:
    """
    Format save-state tag.

    :param tag: Tag to be formatted.

    :returns: Formatted tag.
    """

    if tag != "" and tag[0].isalnum():
        return tag.strip().replace(" ", "-").lower()

    return DATABASE_SAVE_TAG_DEFAULT


# =============================================================================
