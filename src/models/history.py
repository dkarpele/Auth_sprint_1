import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
from db.postgres import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginHistory(Base):
    __tablename__ = 'login_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    user_id = Column(UUID,
                     ForeignKey('users.id', ondelete='CASCADE'),
                     nullable=False)
    source = Column(String(255), default=None)
    login_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self,
                 user_id: UUID,
                 source: str = None,
                 login_time: datetime = datetime.now()) -> None:
        self.user_id = user_id
        self.source = source
        self.login_time = login_time

