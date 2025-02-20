import typing

import rich.progress
import rich.status
import rich.table

from ....display.configs import UI_REFRESH_RATE
from ....display.console import console
from ...context.settings import settings
from ..messages.extract import ExtractSignal as ExtractSignal
from ..messages.primers import Primer
from .types.presenter import Presenter


def present() -> Presenter[tuple[ExtractSignal, float]]:
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
                    refresh_per_second=UI_REFRESH_RATE,
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
                    refresh_per_second=UI_REFRESH_RATE,
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
