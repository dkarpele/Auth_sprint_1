import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base


class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    title = Column(String(255), unique=True, nullable=False)
    permissions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, title: str, permissions: int) -> None:
        self.title = title
        self.permissions = permissions

    def __repr__(self) -> str:
        return f'<Role {self.title}>'


class UserRole(Base):
    __tablename__ = 'users_roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    user_id = Column(UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(UUID, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    user_role_idx = UniqueConstraint('user_id', 'role_id')

    def __init__(self, user_id: UUID, role_id: UUID) -> None:
        self.user_id = user_id
        self.role_id = role_id
