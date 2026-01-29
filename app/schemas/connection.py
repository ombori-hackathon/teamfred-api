from datetime import datetime

from pydantic import BaseModel, field_validator


class ConnectionBase(BaseModel):
    source_id: int
    target_id: int
    label: str | None = None
    connection_type: str = "relates_to"

    @field_validator("connection_type")
    @classmethod
    def validate_connection_type(cls, v: str) -> str:
        allowed = {"relates_to", "depends_on", "contradicts"}
        if v not in allowed:
            raise ValueError(f"connection_type must be one of: {allowed}")
        return v

    @field_validator("target_id")
    @classmethod
    def validate_different_ids(cls, v: int, info) -> int:
        if info.data.get("source_id") == v:
            raise ValueError("source_id and target_id must be different")
        return v


class ConnectionCreate(ConnectionBase):
    pass


class ConnectionUpdate(BaseModel):
    label: str | None = None
    connection_type: str | None = None

    @field_validator("connection_type")
    @classmethod
    def validate_connection_type(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = {"relates_to", "depends_on", "contradicts"}
        if v not in allowed:
            raise ValueError(f"connection_type must be one of: {allowed}")
        return v


class ConnectionResponse(ConnectionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
