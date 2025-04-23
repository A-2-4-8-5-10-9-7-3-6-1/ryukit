"""App implemeentation."""

from . import __typer__
from .install_ryujinx import *
from .save import *

__all__ = ["app"]
app = __typer__.app
