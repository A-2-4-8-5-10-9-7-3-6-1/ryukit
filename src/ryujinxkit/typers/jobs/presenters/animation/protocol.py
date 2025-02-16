"""
- dependency level 0.
"""

import typing


class Protocol(typing.Protocol):
    """
    Typer-widget protocol.
    """

    def start(*args: typing.Any, **kwargs: typing.Any) -> typing.Any: ...

    def stop(*args: typing.Any, **kwargs: typing.Any) -> typing.Any: ...
