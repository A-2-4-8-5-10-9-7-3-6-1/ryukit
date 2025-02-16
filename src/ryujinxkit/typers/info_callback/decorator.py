"""
- dependency level 0.
"""

import collections.abc

import typer


def decorator(
    job: collections.abc.Callable[[], None]
) -> collections.abc.Callable[[bool], None]:
    """
    Get typer-callback pattern for info jobs.

    :param job: An info job.

    :returns: A typer callback for the job.
    """

    def inner(show: bool) -> None:
        if show:
            job()

            raise typer.Exit()

    return inner
