import typing


class AuthorCommandJSON(typing.TypedDict):
    author: str


class VersionCommandJSON(typing.TypedDict):
    version: str


class SaveCreateCommandJSON(typing.TypedDict):
    id: int


class SaveExtractCommandJSON(typing.TypedDict):
    code: typing.NotRequired[typing.Literal["EXTRACTION_ISSUE"]]
    accepted: typing.NotRequired[int]


class SaveTransferCommandJSON(typing.TypedDict):
    code: typing.Literal["ID_ISSUE"]


class SaveRender(typing.TypedDict):
    id: str
    tag: str
    created: str
    updated: str
    used: str | None
    size: str


class SaveListCommandJSON(typing.TypedDict):
    batches: list[list[SaveRender]]
