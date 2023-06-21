import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
from db.postgres import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self,
                 email: str,
                 password: str,
                 first_name: str = None,
                 last_name: str = None,
                 login: str = None) -> None:
        self.login = login if login else email
        self.email = email
        self.password = self.password = pwd_context.hash(password)
        self.first_name = first_name if first_name else ""
        self.last_name = last_name if last_name else ""

    def __repr__(self) -> str:
        return f'<User {self.login}>'
