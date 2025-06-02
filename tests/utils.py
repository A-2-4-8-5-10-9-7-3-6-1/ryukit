"""Common utilities."""

import functools
import os
from typing import Callable

__all__ = ["requires_vars"]


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
