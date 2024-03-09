from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import select, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload

from common.enums import TaskStatus
from common.models import Base, User, Task
from constants import ReportRowProto


class ParamError(Exception):
    pass


DB_URL = "postgresql+psycopg2://admin:admin@postgres:5432/tasktracker"
ASYNC_DB_URL = 'postgresql+asyncpg://admin:admin@postgres:5432/tasktracker'

engine = create_engine(DB_URL)
Base.metadata.create_all(engine)

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def add_user_and_task(user_name: str, task_name: str) -> int:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_name == user_name).with_for_update())
            user = result.scalars().first()

            if not user:
                user = User(user_name=user_name)
                session.add(user)
                await session.flush()

            if user.active_task_id is not None:
                raise ParamError(f"{user_name} already has an active task.")

            task = Task(user_id=user.id, task_name=task_name, status=TaskStatus.active, start_time=datetime.utcnow())
            session.add(task)
            await session.flush()

            user.active_task_id = task.id

            print(f"Added '{task_name}' to user {user_name}.")

            return int(task.id)


async def mark_task_as_finished(user_name: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_name == user_name).options(selectinload(
                User.active_task)))
            user = result.scalars().first()

            if not user:
                raise ParamError(f"{user_name} not found.")

            if user.active_task_id is None or user.active_task is None:
                raise ParamError(f"{user_name} doesn't have an active task.")

            task = user.active_task
            if task.status == TaskStatus.finished:
                raise ParamError(f"{user_name} doesn't have an active task.")

            task.status = TaskStatus.finished
            task.end_time = datetime.utcnow()

            user.active_task_id = None

            print(f"{user_name}'s task '{task.task_name}' marked as finished.")


async def fetch_finished_tasks() -> AsyncGenerator[ReportRowProto, None]:
    """ Async generator for performance and memory efficiency. """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            query = select(
                    User.user_name,
                    Task.task_name,
                    (Task.end_time - Task.start_time).label("duration")) \
                .join(Task, User.id == Task.user_id).filter(Task.status == TaskStatus.finished) \
                .order_by(User.user_name, Task.start_time)

            result_stream = await session.stream(query)
            async for row in result_stream:
                yield row
