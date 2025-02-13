"""
- dependency level 0.
"""

import collections.abc


class Formatter[T, R]:
    """
    Formatter class for function parameters.
    """

    def __init__(self, function: collections.abc.Callable[[T], R]) -> None:
        """
        Instantiate a formatter.

        :param function: The formatting function.
        """

        self._function = function

    def __call__(self, input_: T) -> R:
        """
        Use formatter.

        :param %input_%: Input to format.

        :returns: Formatted input.
        """

        return self._function(input_)
