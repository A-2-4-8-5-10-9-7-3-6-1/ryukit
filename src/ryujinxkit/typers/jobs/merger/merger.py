"""
- dependency level 1.
"""

import collections.abc

from .protocol import Merger


def _null_presenter() -> collections.abc.Generator[None]:
    """
    A dumb presenter.
    """

    yield


def merger[
    **P,
    R,
    I,
](
    action: collections.abc.Callable[P, R],
    presenter: collections.abc.Callable[
        [],
        collections.abc.Generator[None, I],
    ] = _null_presenter,
) -> collections.abc.Callable[
    [Merger[R, I]],
    collections.abc.Callable[P, None],
]:
    """
    Combine an action, presenter, and merger into a task.

    :param action: A selected action.
    :param presenter: A selected presenter.

    :returns: A decorator, to collect the merger.
    """

    pole = presenter()

    def decorator(merger: Merger[R, I]) -> collections.abc.Callable[P, None]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> None:
            next(pole)

            try:
                merger(in_=action(*args, **kwargs), pole=pole)

            except StopIteration:
                pass

            finally:
                pole.close()

        return inner

    return decorator
