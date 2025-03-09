"""Symbols for the realization of the action-presenter decompoition of commands.

Exports
-------
- :func:`merger`: The method through which actions and presenters are coupled.
- :class:`PrimitiveSignal`: Primitive signals, for presenters.
"""

import collections.abc
import enum
import typing


class PrimitiveSignal(int, enum.Enum):
    """
    Primitive signals, for presenters.
    """

    FINISHED = 0
    KILL = 1


class Merger[T, I](typing.Protocol):
    def __call__(
        self,
        in_: T,
        pole: collections.abc.Generator[typing.Any, I | PrimitiveSignal],
    ) -> None: ...


def merger[**P, R, I](
    action: collections.abc.Callable[P, R],
    presenter: collections.abc.Callable[
        [], collections.abc.Generator[typing.Any, I | PrimitiveSignal]
    ],
) -> collections.abc.Callable[
    [Merger[R, I]], collections.abc.Callable[P, None]
]:
    """
    Combine an action, presenter, and merger into a task.

    :param action: A selected action.
    :param presenter: A selected presenter.

    :returns: A decorator, to collect the merger.
    """

    pole = presenter()

    def decorator(function: Merger[R, I]) -> collections.abc.Callable[P, None]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> None:
            try:
                next(pole)

                try:
                    function(in_=action(*args, **kwargs), pole=pole)

                except KeyboardInterrupt:
                    pole.send(PrimitiveSignal.KILL)

            except StopIteration:
                pass

            finally:
                pole.close()

        return inner

    return decorator
