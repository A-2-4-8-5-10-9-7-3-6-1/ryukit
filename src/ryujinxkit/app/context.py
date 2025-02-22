import typing


class _Settings(typing.TypedDict):
    json: bool


settings: _Settings = {
    "json": False,
}
