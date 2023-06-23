from uuid import UUID

from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    title: str = Field(..., max_length=50)
    permissions: int = 0


class RoleInDB(BaseModel):
    id: UUID
    title: str
    permissions: int

    class Config:
        orm_mode = True
