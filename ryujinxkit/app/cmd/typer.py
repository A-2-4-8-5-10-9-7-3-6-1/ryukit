"""Defines the root typer."""

import importlib
import importlib.metadata

import typer

from ...core.ui.theme_applier import styled

app_typer = styled(typer.Typer)(
    name="ryujinxkit",
    invoke_without_command=True,
    help=f"{importlib.metadata.metadata("ryujinxkit")["summary"]}"
    " Invoke without argument to install Ryujinx.",
)
