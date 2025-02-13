"""
- dependency level 0.
"""

import collections.abc
import inspect
import typing

from .formatter import Formatter


def apply_formatters[
    **P,
    T,
](function: collections.abc.Callable[P, T]) -> collections.abc.Callable[P, T]:
    """
    Apply formatters to args for pre-processing.

    :param function: Function to apply formatting on.
    :param formatters: Parameter formatters.

    :returns: Ammended version of input function.
    """

    sgn = inspect.signature(obj=function)
    annotations = typing.get_type_hints(obj=function, include_extras=True)

    def decorator(*args: P.args, **kwargs: P.kwargs) -> T:
        bound_args = sgn.bind(*args, **kwargs)

        bound_args.apply_defaults()

        for k, v in bound_args.arguments.items():
            if not (
                k in annotations and hasattr(annotations[k], "__metadata__")
            ):
                continue

            for formatter in annotations[k].__metadata__:
                if not isinstance(formatter, Formatter):
                    continue

                bound_args.arguments[k] = formatter(input_=v)

        return function(*bound_args.args, **bound_args.kwargs)

    return decorator
