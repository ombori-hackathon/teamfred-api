from datetime import datetime

from pydantic import BaseModel


class TagBase(BaseModel):
    name: str
    color: str = "#6b7280"


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
