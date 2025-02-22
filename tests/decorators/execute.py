import collections
import collections.abc
import subprocess
import typing


def execute[**P, R](*args: str) -> collections.abc.Callable[
    [
        collections.abc.Callable[
            typing.Concatenate[subprocess.CompletedProcess[str], P],
            R,
        ]
    ],
    collections.abc.Callable[P, R],
]:
    """
    Execute a Shell command.

    :param args: The command, divided by args.

    :returns: The results of the execution.
    """

    def decorator(
        function: collections.abc.Callable[
            typing.Concatenate[subprocess.CompletedProcess[str], P],
            R,
        ]
    ) -> collections.abc.Callable[P, R]:
        def inner(*i_args: P.args, **kwargs: P.kwargs) -> R:
            results = subprocess.run(args=args, capture_output=True, text=True)

            assert results.returncode == 0

            return function(results, *i_args, **kwargs)

        return inner

    return decorator
