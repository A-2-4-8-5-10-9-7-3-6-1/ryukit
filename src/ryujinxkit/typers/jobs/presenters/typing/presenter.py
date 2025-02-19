import collections.abc
import typing

from ..enums.commands import Enum as Command

type Presenter[T] = collections.abc.Generator[typing.Any, T | Command]
