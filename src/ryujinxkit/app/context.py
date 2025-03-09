"""'App context'-related symbols.

Exports
-------
- settings: Session settings.
"""

import typing


class Settings(typing.TypedDict):
    json: bool


settings: Settings = {"json": False}
