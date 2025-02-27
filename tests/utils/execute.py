import subprocess


def execute(*args: str) -> subprocess.CompletedProcess[str]:
    """
    Execute a subprocess, doing default tests in the background.

    :param args: Arguments for shell interaction.

    :returns: The results of process execution.

    :raises AssertionError: If default tests are failed.
    """

    results = subprocess.run(args=args, capture_output=True, text=True)

    assert results.returncode == 0

    return results
