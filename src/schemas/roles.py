from uuid import UUID

from pydantic import BaseModel


class RoleCreate(BaseModel):
    title: str = None
    permissions: int = None


class RoleInDB(BaseModel):
    id: UUID
    title: str
    permissions: int

    class Config:
        orm_mode = True
