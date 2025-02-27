import collections.abc
import typing

from ..annotations import Presenter
from ..signals import Primer


class _Merger[T, I](typing.Protocol):
    def __call__(self, in_: T, pole: Presenter[I]) -> None: ...


def merger[
    **P,
    R,
    I,
](
    action: collections.abc.Callable[P, R],
    presenter: collections.abc.Callable[[], Presenter[I]],
) -> collections.abc.Callable[
    [_Merger[R, I]],
    collections.abc.Callable[P, None],
]:
    """
    Combine an action, presenter, and merger into a task.

    :param action: A selected action.
    :param presenter: A selected presenter.

    :returns: A decorator, to collect the merger.
    """

    pole = presenter()

    def decorator(
        function: _Merger[R, I]
    ) -> collections.abc.Callable[P, None]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> None:
            try:
                next(pole)

                try:
                    function(in_=action(*args, **kwargs), pole=pole)

                except KeyboardInterrupt:
                    pole.send(Primer.KILL)

            except StopIteration:
                pass

            finally:
                pole.close()

        return inner

    return decorator
