from ....display.console import console
from ...context.settings import settings
from ..messages.primers import Primer
from .types.presenter import Presenter


def present() -> Presenter[str]:
    """
    Present information from the version action.
    """

    signal = yield

    if isinstance(signal, Primer):
        return

    if settings["json"]:
        return console.print_json(
            data={
                "version": signal,
            }
        )

    console.print(f"(RyujinxKit) version {signal}")
