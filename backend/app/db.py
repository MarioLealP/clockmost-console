from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import get_settings

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def engine() -> AsyncEngine:
    global _engine, _sessionmaker  # noqa: PLW0603
    if _engine is None:
        _engine = create_async_engine(get_settings().database_url, echo=False, future=True)
        _sessionmaker = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _engine


async def get_session() -> AsyncIterator[AsyncSession]:
    engine()
    assert _sessionmaker is not None
    async with _sessionmaker() as session:
        yield session


async def dispose_engine() -> None:
    global _engine, _sessionmaker  # noqa: PLW0603
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _sessionmaker = None


SessionDep = Annotated[AsyncSession, Depends(get_session)]
