# TODO: create models for API responses for type safety, consistent data contracts
from pydantic import BaseModel
from datetime import date


class AuthorResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes: bool = True


class PEPResponse(BaseModel):
    number: int
    title: str
    status: str
    type: str
    topic: str
    created: date | None
    python_version: str | None
    url: str
    authors: list[AuthorResponse]

    class Config:
        from_attributes: bool = True


class PEPListResponse(BaseModel):
    peps: list[PEPResponse]
    total: int
    skip: int
    limit: int

