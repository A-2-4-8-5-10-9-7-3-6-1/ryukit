import rich.progress

from ....display.configs import UI_REFRESH_RATE
from ....display.console import console
from ...context.settings import settings
from ..messages.extract import ExtractSignal as ExtractSignal
from ..messages.primers import Primer
from .animation.protocol import Protocol as Animation
from .types.presenter import Presenter


def present() -> Presenter[tuple[ExtractSignal, float]]:
    """
    Present information from the extract command.
    """

    looping: bool = False
    animation: Animation | None = None
    task_id: rich.progress.TaskID
    r_total: float

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

                animation.stop()  # type: ignore

                if settings["json"]:
                    return console.print_json(
                        data={
                            "code": "EXTRACTION_ISSUE",
                        }
                    )

                return console.print("Malformed export file.")

            case ExtractSignal.READING, volume:
                if looping:
                    animation.advance(task_id=task_id, advance=volume)  # type: ignore

                    continue

                animation.stop()  # type: ignore

                animation = rich.progress.Progress(
                    rich.progress.SpinnerColumn(style="dim"),
                    "[dim]{task.description}",
                    "[dim]({task.percentage:.1f}%)",
                    console=console,
                    refresh_per_second=UI_REFRESH_RATE,
                    transient=True,
                )
                task_id = animation.add_task(
                    description="Reading", total=volume
                )
                r_total = volume
                looping = True

                animation.start()

            case Primer.FINISHED:
                looping = False

                animation.stop()  # type: ignore

                if settings["json"]:
                    return console.print_json(
                        data={
                            "code": "SUCCESS",
                            "accepted": r_total,  # type: ignore
                        }
                    )

                return console.print(f"Accepted {r_total} save instance(s).")  # type: ignore

            case Primer.KILL:
                if animation is not None:
                    animation.stop()

                return

            case _:
                pass
