from .helpers import typer_builder

__all__ = ["start"]
start = lambda: app()
app = typer_builder.build_typer("app")
