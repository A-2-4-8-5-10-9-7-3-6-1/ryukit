import json
import typing

import rich.progress

from .....libs.jobs.annotations import Presenter
from .....libs.jobs.signals import Primer
from .....libs.ui.configs import UI_CONFIGS
from .....libs.ui.console import console
from ....context import settings
from .signals import StateTransferSignal


def presenter() -> Presenter[tuple[StateTransferSignal, float]]:
    looping = False
    animation: rich.progress.Progress | None = None
    task_id: rich.progress.TaskID | None = None

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
                    typing.cast(rich.progress.Progress, animation).advance(
                        task_id=typing.cast(rich.progress.TaskID, task_id),
                        advance=volume,
                    )

                    continue

                animation = rich.progress.Progress(
                    rich.progress.SpinnerColumn(style="dim"),
                    "[dim]{task.description}",
                    "[dim]({task.completed}/{task.total})",
                    console=console,
                    refresh_per_second=UI_CONFIGS["refresh_rate"],
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

                typing.cast(rich.progress.Progress, animation).stop()

                if settings["json"]:
                    return console.print(
                        json.dumps(
                            {
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
