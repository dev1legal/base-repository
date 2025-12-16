from __future__ import annotations

import base64
import json
from typing import Any, TypeVar

from litestar.params import Parameter
from pydantic import BaseModel

from base_repository.query.list_query import ListQuery
from base_repository.repo_types import TModel

T = TypeVar('T', bound=ListQuery[Any])


class OffsetPagination(BaseModel):
    page: int = Parameter(ge=1, default=1, query='page', description='Page number')
    size: int = Parameter(ge=1, default=20, query='size', description='Page size')


class CursorPagination(BaseModel):
    cursor: str | None = Parameter(
        default=None,
        query='cursor',
        description='Cursor string (base64 encoded JSON) for keyset pagination',
    )
    limit: int = Parameter(ge=1, default=20, query='limit', description='Page limit')


def provide_offset_pagination(
    page: int = Parameter(ge=1, default=1, query='page', description='Page number'),
    size: int = Parameter(ge=1, default=20, query='size', description='Page size'),
) -> OffsetPagination:
    return OffsetPagination(page=page, size=size)


def provide_cursor_pagination(
    cursor: str | None = Parameter(
        default=None,
        query='cursor',
        description='Cursor string (base64 encoded JSON) for keyset pagination',
    ),
    limit: int = Parameter(ge=1, default=20, query='limit', description='Page limit'),
) -> CursorPagination:
    return CursorPagination(cursor=cursor, limit=limit)


def apply_pagination(q: ListQuery[TModel], pagination: OffsetPagination | CursorPagination) -> ListQuery[TModel]:
    """
    Apply pagination parameters to the ListQuery.
    """
    if isinstance(pagination, OffsetPagination):
        return q.paging(page=pagination.page, size=pagination.size)

    if isinstance(pagination, CursorPagination):
        cursor_dict: dict[str, Any] | None = None
        if pagination.cursor:
            try:
                decoded = base64.urlsafe_b64decode(pagination.cursor).decode('utf-8')
                cursor_dict = json.loads(decoded)
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                # If decoding fails, treating it as invalid cursor or empty.
                # For safety, let's pass empty dict if decoding failed?
                # Or maybe we shouldn't swallow errors silently?
                # Given this is a helper, raising an error might be 500.
                # Let's fallback to None (start) or empty.
                cursor_dict = {}

        q.with_cursor(cursor_dict or {})
        q.limit(pagination.limit)
        return q

    return q
