"""
- dependency level 1.
"""

from argparse import Namespace
from typing import Callable

from ...general import DATABASE_SAVE_TAG_DEFAULT, Command, T
from ..constants.configs import DEFAULT_ARCHIVE_NAME

# =============================================================================


def _format_tag(tag: str) -> str:
    """
    Format save-state tag.

    :param tag: Tag to be formatted.

    :returns: Formatted tag.
    """

    if tag != "" and tag[0].isalnum():
        return tag.strip().replace(" ", "-").lower()

    return DATABASE_SAVE_TAG_DEFAULT


# -----------------------------------------------------------------------------

_INPUT_FORMATTERS: dict[Command, list[tuple[str, Callable[[T], T]]]] = {
    Command.RYUJINXKIT_SAVE_CREATE: [("tag", _format_tag)],
    Command.RYUJINXKIT_SAVE_EXPORT: [
        ("output", lambda name: name if name != "" else DEFAULT_ARCHIVE_NAME)
    ],
    Command.RYUJINXKIT_SAVE_RETAG: [("tag", _format_tag)],
}

# -----------------------------------------------------------------------------


def sanitize(
    command: Command,
    function: Callable[[Namespace], T],
) -> Callable[[Namespace], T]:
    """
    Sanitize command functions.

    :param command: Command to sanitize for.
    :param function: `command`'s function.

    :returns: A sanitized version of `function`.
    """

    if command not in _INPUT_FORMATTERS:
        return function

    def inner(namespace: Namespace) -> T:
        [
            setattr(namespace, key, sanitizer(getattr(namespace, key)))
            for key, sanitizer in _INPUT_FORMATTERS[command]
        ]

        return function(namespace)

    return inner


# =============================================================================
