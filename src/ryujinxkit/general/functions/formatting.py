"""
- dependency level 1.
"""

from typing import Callable, Iterable, ParamSpec, TypeVar

from ..constants.configs import DATABASE_SAVE_TAG_DEFAULT

# =============================================================================

_P = ParamSpec(name="P")
_T = TypeVar(name="T")
_U = TypeVar(name="U")

# -----------------------------------------------------------------------------


def format_tag(tag: str) -> str:
    """
    Format save-state tag.

    :param tag: Tag to be formatted.

    :returns: Formatted tag.
    """

    if tag != "" and tag[0].isalnum():
        return tag.strip().replace(" ", "-").lower()

    return DATABASE_SAVE_TAG_DEFAULT


# -----------------------------------------------------------------------------


def apply_formatters(
    formatters: Iterable[tuple[str, Callable[[_T], _T]]] = [],
) -> Callable[[Callable[_P, _U]], Callable[_P, _U]]:
    """
    Apply formatters to args for pre-processing.

    :param function: Function to apply formatting on.
    :param formatters: Parameter formatters.

    :returns: Ammended version of input function.
    """

    return lambda function: lambda *args, **kwargs: [
        [kwargs.__setitem__(k, f(kwargs[k])) for k, f in formatters],
        function(*args, **kwargs),
    ][1]


# =============================================================================
