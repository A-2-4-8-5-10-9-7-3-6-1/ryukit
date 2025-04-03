"""Entrypoint script."""

from .app.cmd._callback_ import *
from .app.cmd.install_ryujinx import *
from .app.cmd.manage._callback_ import *
from .app.cmd.manage.save_control.create import *
from .app.modules import context


def entrypoint():
    context.root_typer()


if __name__ == "__main__":
    entrypoint()
