"""Common utilities."""

import contextlib
import functools
import io
import os
import sys
from typing import Callable

__all__ = ["capture_out", "requires_vars"]


@contextlib.contextmanager
def capture_out():
    """Capture sys.stdout output within context."""

    register: list[str] = []
    with io.StringIO() as buffer:
        sys.stdout = buffer
        yield register
        sys.stdout = sys.__stdout__
        register.append(buffer.getvalue())


def requires_vars(*vars: str):
    """
    Mark a function as requiring env vars.

    :param vars: The variables required.
    """

    def inner[**P, R](func: Callable[P, R]):
        @functools.wraps(func)
        def core(*args: P.args, **kwargs: P.kwargs):
            for var in vars:
                if os.environ.get(var):
                    continue
                raise RuntimeError(f"Missing variable '{var}'.")
            return func(*args, **kwargs)

        return core

    return inner
