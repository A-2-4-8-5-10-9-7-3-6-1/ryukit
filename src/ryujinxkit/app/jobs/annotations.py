import collections.abc
import typing

from .signals import Primer

type Presenter[T] = collections.abc.Generator[typing.Any, T | Primer]
