"""
- dependency level 0.
"""

from typing import Callable, Iterable, ParamSpec, TypeVar

# =============================================================================

_P = ParamSpec(name="P")
_T = TypeVar(name="T")
_U = TypeVar(name="U")

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
