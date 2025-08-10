from sqlalchemy import Column, DateTime, Integer, String
from framework.db import Base
from datetime import datetime, UTC
from pydantic import BaseModel

class ${{values.app_name}}(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    create_date = Column(DateTime, default=lambda: datetime.now(UTC))
    update_date = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)  # auto-update on change
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class ${{values.app_name}}Create(BaseModel):
    username: str
    email: str