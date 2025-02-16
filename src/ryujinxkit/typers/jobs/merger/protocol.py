"""
- dependency level 0.
"""

import collections.abc
import typing


class Merger[T, I](typing.Protocol):
    """
    Merger protocol.
    """

    def __call__(
        self,
        in_: T,
        pole: collections.abc.Generator[None, I],
    ) -> None: ...
