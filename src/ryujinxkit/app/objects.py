"""
- dependency level 0.
"""

import typing

import rich.console


class Objects:
    """
    Class for object storage.

    :attr console: Main `rich.Console` instance.
    """

    console: typing.ClassVar[rich.console.Console] = rich.console.Console(
        highlight=False
    )

    def __init__(self) -> typing.Never:
        """
        :raises: `NotImplementedError` on attempted invokation.
        """

        raise NotImplementedError
