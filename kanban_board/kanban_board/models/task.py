from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from .meta import Base

TYPES = ["TODO", "PROGRESS", "DONE"]


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    content = Column(Text)
    state = Column(Text, default=TYPES[0])
