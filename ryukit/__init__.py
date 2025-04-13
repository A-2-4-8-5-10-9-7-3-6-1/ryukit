from .core import runtime
from .utils import typer_builder

__all__ = ["start"]
start = lambda: runtime.with_context(app)()
app = typer_builder.build_typer("app")
