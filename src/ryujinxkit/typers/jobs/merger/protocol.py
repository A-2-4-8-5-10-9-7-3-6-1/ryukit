import typing

from ..presenters.types.presenter import Presenter


class Protocol[T, I](typing.Protocol):
    """
    Merger protocol.
    """

    def __call__(self, in_: T, pole: Presenter[I]) -> None: ...
