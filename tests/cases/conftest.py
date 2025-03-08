import pytest

from ..utils.context_control import destroy_context

__all__ = []


@pytest.fixture(autouse=True)
def _():
    """
    Destroy file-system context from previous tests.
    """

    destroy_context()

    yield
