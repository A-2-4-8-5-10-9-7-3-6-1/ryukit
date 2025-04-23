from . import app
from .core import runtime

__all__ = ["start"]
start = lambda: runtime.with_context(app.app)()
