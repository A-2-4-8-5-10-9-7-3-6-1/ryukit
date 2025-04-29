"""Execution-orchestration tools."""

import collections
import collections.abc
import functools

__all__ = ["and_packup", "packup_callback"]
type PackupCallback = collections.abc.Callable[[], object]
packup_callbacks: list[PackupCallback] = []


def and_packup[**P, R](
    func: collections.abc.Callable[P, R],
) -> collections.abc.Callable[P, R]:
    """
    Tag packup logic onto 'func'.

    :param func: The function to extend.
    :returns: 'func' with embedded packup logic.
    """

    @functools.wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            any(packup() and False for packup in packup_callbacks)

    return inner


def packup_callback(callback: PackupCallback):
    """
    Mark 'callback' as a packup callback.

    :param callback: The callback to mark.
    """

    packup_callbacks.append(callback)
    return callback
