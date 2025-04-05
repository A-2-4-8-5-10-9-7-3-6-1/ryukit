from .helpers import builders

__all__ = ["start"]
start = lambda: app()
app = builders.typer_from_dir("app")
