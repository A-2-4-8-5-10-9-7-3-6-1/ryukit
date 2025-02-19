import collections.abc
import typing

from ...messages.primers import Primer

type Presenter[T] = collections.abc.Generator[typing.Any, T | Primer]
