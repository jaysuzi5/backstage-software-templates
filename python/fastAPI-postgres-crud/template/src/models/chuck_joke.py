from sqlalchemy import Column, DateTime, Integer, String
from framework.db import Base
from datetime import datetime, UTC

class ChuckJoke(Base):
    __tablename__ = 'chuck_jokes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    joke = Column(String, unique=True, nullable=False)
    create_date = Column(DateTime, default=lambda: datetime.now(UTC))