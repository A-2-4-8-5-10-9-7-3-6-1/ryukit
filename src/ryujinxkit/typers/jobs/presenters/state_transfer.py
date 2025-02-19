import json

import rich.progress

from ....display.configs import UI_REFRESH_RATE
from ....display.console import console
from ...context.settings import settings
from ..messages.primers import Primer
from ..messages.state_transfer import StateTransferSignal
from .animation.protocol import Protocol as Animation
from .types.presenter import Presenter


def present() -> Presenter[tuple[StateTransferSignal, float]]:
    """
    Present information from save-transfer actions.
    """

    looping: bool = False
    animation: Animation | None = None
    task_id: rich.progress.TaskID

    while True:
        match (yield):
            case StateTransferSignal.FAILED, 0:
                if settings["json"]:
                    return console.print_json(
                        data={
                            "code": "ID_ISSUE",
                        }
                    )

                return console.print("Unrecognized save ID.")

            case StateTransferSignal.TRANSFERING, volume:
                if looping:
                    animation.advance(task_id=task_id, advance=volume)  # type: ignore

                    continue

                animation = rich.progress.Progress(
                    rich.progress.SpinnerColumn(style="dim"),
                    "[dim]{task.description}",
                    "[dim]({task.completed}/{task.total})",
                    console=console,
                    refresh_per_second=UI_REFRESH_RATE,
                    transient=True,
                )
                task_id = animation.add_task(
                    description="Transfering",
                    total=volume,
                )
                looping = True

                animation.start()

            case Primer.FINISHED:
                looping = False

                animation.stop()  # type: ignore

                if settings["json"]:
                    return console.print(
                        json.dumps(
                            obj={
                                "code": "SUCCESS",
                            }
                        )
                    )

                return console.print("Transfer successful.")

            case Primer.KILL:
                if animation is not None:
                    animation.stop()

                return

            case _:
                pass
