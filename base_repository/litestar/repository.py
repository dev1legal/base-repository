from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from base_repository.repository.base_repo import BaseRepository

T = TypeVar('T', bound=BaseRepository)


def provide_repo(repo_type: type[T]) -> Callable[[AsyncSession], Awaitable[T]]:
    """
    Create a dependency provider for a specific Repository type.

    Usage:
        app = Litestar(
            dependencies={
                "user_repo": Provide(provide_repo(UserRepository)),
            }
        )
    """

    async def _provide_repo(session: AsyncSession) -> T:
        return repo_type(session=session)

    return _provide_repo
