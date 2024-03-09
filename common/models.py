from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import declarative_base, relationship

from common.enums import TaskStatus

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String, unique=True, index=True)
    active_task_id = Column(Integer, ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True)
    active_task = relationship("Task", foreign_keys=[active_task_id], backref="user", uselist=False)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    task_name = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.active)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
