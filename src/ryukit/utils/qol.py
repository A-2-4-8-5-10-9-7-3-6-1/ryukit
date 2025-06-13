"""Quality-of-life utilities."""

from collections.abc import Callable
from typing import Any

__all__ = ["in_dict", "use"]


def in_dict[K, V: Callable[..., Any]](dict_: dict[K, V], /, key: K):
    """
    Manage function-valued dictionary entries with a decorator.

    :param dict_: The dictionary to manage.
    :param key: A key to store the subsequent function under.
    """

    def inner(func: V):
        dict_[key] = func
        return func

    return inner


def use[R](func: Callable[..., R], /):
    """Immediately use a function."""

    return func()
