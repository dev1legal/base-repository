import base64
import json
from typing import Any
from unittest.mock import MagicMock

from litestar import Litestar, get
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK
from litestar.testing import TestClient
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from base_repository.litestar import (
    CursorPagination,
    OffsetPagination,
    apply_pagination,
    provide_cursor_pagination,
    provide_offset_pagination,
    provide_repo,
)
from base_repository.repository import BaseRepository
from tests.models import Item


class ItemSchema(BaseModel):
    model_config = {'from_attributes': True}
    id: int
    name: str


class ItemRepo(BaseRepository[Item, ItemSchema]):
    pass


def test_provide_repo_di() -> None:
    @get('/', dependencies={'repo': Provide(provide_repo(ItemRepo))})
    async def handler(repo: ItemRepo) -> None:
        assert isinstance(repo, ItemRepo)
        assert repo.session is not None

    async def get_session() -> MagicMock:
        # Fake session provider for test
        return MagicMock(spec=AsyncSession)

    app = Litestar(
        route_handlers=[handler],
        dependencies={'session': Provide(get_session)},
        debug=True,
    )

    with TestClient(app=app) as client:
        res = client.get('/')
        if res.status_code != HTTP_200_OK:
            print(f'Test provide_repo failed: {res.status_code} {res.text}')
        assert res.status_code == HTTP_200_OK


def test_apply_pagination_offset() -> None:
    repo = ItemRepo()
    q = repo.list()
    p = OffsetPagination(page=2, size=10)

    q2 = apply_pagination(q, p)

    assert q2.page == 2
    assert q2.offset_size == 10


def test_apply_pagination_cursor() -> None:
    repo = ItemRepo()
    q = repo.list().order_by(['id'])  # type: ignore

    cursor_data = {'id': 10}
    cursor_str = base64.urlsafe_b64encode(json.dumps(cursor_data).encode()).decode('utf-8')

    p = CursorPagination(cursor=cursor_str, limit=5)

    q2 = apply_pagination(q, p)

    assert q2.cursor == cursor_data
    assert q2.cursor_size == 5


def test_controller_integration_offset() -> None:
    @get('/', dependencies={'params': Provide(provide_offset_pagination, sync_to_thread=False)})
    async def handler(params: OffsetPagination) -> dict[str, Any]:
        return params.model_dump()

    with TestClient(app=Litestar(route_handlers=[handler], debug=True)) as client:
        res = client.get('/', params={'page': '3', 'size': '50'})
        if res.status_code != HTTP_200_OK:
            print(f'Test offset failed: {res.status_code} {res.text}')
        assert res.status_code == HTTP_200_OK
        data = res.json()
        assert data['page'] == 3
        assert data['size'] == 50


def test_controller_integration_cursor() -> None:
    @get('/', dependencies={'params': Provide(provide_cursor_pagination, sync_to_thread=False)})
    async def handler(params: CursorPagination) -> dict[str, Any]:
        return params.model_dump()

    with TestClient(app=Litestar(route_handlers=[handler], debug=True)) as client:
        res = client.get('/', params={'cursor': 'abcd', 'limit': '15'})
        if res.status_code != HTTP_200_OK:
            print(f'Test cursor failed: {res.status_code} {res.text}')
        assert res.status_code == HTTP_200_OK
        data = res.json()
        assert data['cursor'] == 'abcd'
        assert data['limit'] == 15
