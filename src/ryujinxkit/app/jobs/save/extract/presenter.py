import typing

import rich.progress
import rich.status
import rich.table

from .....core.ui.configs import UI_CONFIGS
from .....core.ui.console import console
from ....context import settings
from ...annotations import Presenter
from ...signals import Primer
from .signals import ExtractSignal


def presenter() -> Presenter[tuple[ExtractSignal, float]]:
    looping = False
    animation: rich.progress.Progress | rich.status.Status | None = None
    task_id: rich.progress.TaskID | None = None
    r_total: float | None = None

    while True:
        match (yield):
            case ExtractSignal.EXTRACTING, 0:
                animation = console.status(
                    status="Extracting",
                    spinner_style="dim",
                    refresh_per_second=UI_CONFIGS["refresh_rate"],
                )

                animation.start()

            case ExtractSignal.FAILED, 0:
                looping = False

                typing.cast(rich.status.Status, animation).stop()

                if settings["json"]:
                    return console.print_json(
                        data={
                            "code": "EXTRACTION_ISSUE",
                        }
                    )

                return console.print("Malformed export file.")

            case ExtractSignal.READING, volume:
                if looping:
                    animation = typing.cast(
                        rich.progress.Progress,
                        animation,
                    ).advance(
                        task_id=typing.cast(rich.progress.TaskID, task_id),
                        advance=volume,
                    )

                    continue

                typing.cast(rich.status.Status, animation).stop()

                animation = rich.progress.Progress(
                    rich.progress.SpinnerColumn(style="dim"),
                    "[dim]{task.description}",
                    "[dim]({task.percentage:.1f}%)",
                    console=console,
                    refresh_per_second=UI_CONFIGS["refresh_rate"],
                    transient=True,
                )
                task_id = animation.add_task(
                    description="Reading",
                    total=volume,
                )
                r_total = volume
                looping = True

                animation.start()

            case Primer.FINISHED:
                looping = False
                r_total = typing.cast(int, r_total)

                typing.cast(rich.progress.Progress, animation).stop()

                if settings["json"]:
                    return console.print_json(
                        data={
                            "code": "SUCCESS",
                            "accepted": r_total,
                        }
                    )

                return console.print(f"Accepted {r_total} save instance(s).")

            case Primer.KILL:
                if animation is not None:
                    animation.stop()

                return

            case _:
                pass
