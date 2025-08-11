# TODO: create models for API responses for type safety, consistent data contracts
from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class AuthorResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class PEPResponse(BaseModel):
    number: int
    title: str
    status: str
    type: str
    topic: str
    created: Optional[date]
    python_version: Optional[str]
    url: str
    authors: List[AuthorResponse]
    
    class Config:
        from_attributes = True

class PEPListResponse(BaseModel):
    peps: List[PEPResponse]
    total: int
    skip: int
    limit: int