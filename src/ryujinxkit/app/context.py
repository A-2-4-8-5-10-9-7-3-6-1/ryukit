import typing

__all__ = ["settings"]


class Settings(typing.TypedDict):
    json: bool


settings: Settings = {"json": False}
