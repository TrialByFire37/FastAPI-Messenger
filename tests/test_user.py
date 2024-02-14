import pytest
from sqlalchemy import insert, select

from auth.models import User
from user.crud import get_user_by_id
from conftest import client, async_session_maker
from user.schemas import UserReadRequest


async def test_add_user():
    async with async_session_maker() as session:
        stmt = insert(User).values(username="Gelo123g",
                                   email="popov@mail.ru",
                                   hashed_password="123456")
        await session.execute(stmt)
        await session.commit()

        query = select(User)
        result = await session.execute(query)
        print(result.all())
        assert result.all() == [(1, 'Gelo123g', None)], "User не добавилась"


async def test_get_user_by_id():
    async with async_session_maker() as session:
        current_user: UserReadRequest = await get_user_by_id(session, 1)
        assert current_user is not None
        assert current_user.user_id == 1
        assert current_user.username == "Gelo123g"
        assert current_user.email == "popov@mail.ru"
        assert current_user.image_url is None
