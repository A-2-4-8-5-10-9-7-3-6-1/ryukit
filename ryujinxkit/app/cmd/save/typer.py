"Save-typer definition."

import typer

from ....core.ui.theme_applier import styled
from ..typer import app_typer

save_typer = styled(typer.Typer)(invoke_without_command=True)

app_typer.add_typer(
    typer_instance=save_typer, name="save", epilog="Aliases: sv"
)
app_typer.add_typer(typer_instance=save_typer, name="sv", hidden=True)
