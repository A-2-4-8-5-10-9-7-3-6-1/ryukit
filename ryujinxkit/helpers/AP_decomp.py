"""Symbols for the realization of the action-presenter decompoition of commands."""

import collections.abc
import enum
import typing

type Action[ReturnSignal] = collections.abc.Generator[
    ReturnSignal, object, object
]


class PrimitiveSignal(int, enum.Enum):
    FINISHED = 0
    KILL = 1
    START = 2


type Presenter[InputSignal] = collections.abc.Generator[
    object, InputSignal | PrimitiveSignal, typing.Never
]


def merge[**P, Signal](
    action_dispensor: collections.abc.Callable[P, Action[Signal]],
    presenter: Presenter[Signal],
) -> collections.abc.Callable[P, object]:
    """Combine an action, presenter, and merger into a task.

    :param merger: The merger unit.

    :returns: A function, for completing the union.
    """

    def inner(*args: P.args, **kwargs: P.kwargs):
        try:
            next(presenter)
            presenter.send(PrimitiveSignal.START)

            for message in action_dispensor(*args, **kwargs):
                presenter.send(message)

                if message != PrimitiveSignal.KILL:
                    continue

                exit(1)

            presenter.send(PrimitiveSignal.FINISHED)

        except KeyboardInterrupt:
            presenter.send(PrimitiveSignal.KILL)

        finally:
            presenter.close()

    return inner
