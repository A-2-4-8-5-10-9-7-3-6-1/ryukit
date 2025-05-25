"""Common utilities."""

import contextlib
import io
import sys

__all__ = ["capture_out"]


@contextlib.contextmanager
def capture_out():
    """Capture sys.stdout output within context."""

    register: list[str] = []
    with io.StringIO() as buffer:
        sys.stdout = buffer
        yield register
        sys.stdout = sys.__stdout__
        register.append(buffer.getvalue())
