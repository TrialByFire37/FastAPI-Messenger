import asyncio
from datetime import datetime
from typing import List
from unittest.mock import Mock, AsyncMock, MagicMock, call, ANY, patch

import pytest
from fastapi import UploadFile
from httpx import AsyncClient
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound

from auth.schemas import UserRead
from aws.schemas import FileRead
from models.models import user, room_user
from user.crud import get_user_by_id, get_user_by_username, get_users_in_room, update_user_image
from user.schemas import UserReadRequest, UserBaseReadRequest


async def test_get_user_by_id(mock_db_session):
    # Создаем мок для результата запроса к базе данных
    user_instance = MagicMock()
    user_instance.id = 1
    user_instance.username = 'gelo21region'
    user_instance.email = 'popov.gleb.01@mail.ru'
    user_instance.image_url = None
    user_instance.one.return_value = user_instance

    # Устанавливаем моки для сессии и результата запроса
    mock_db_session.execute.return_value = user_instance
    mock_db_session.commit.return_value = None

    # Вызываем функцию и получаем результат
    result = await get_user_by_id(mock_db_session, 1)

    assert result is not None
    # Проверяем, что результат соответствует ожидаемому
    assert isinstance(result, UserReadRequest)
    assert result.user_id == user_instance.id
    assert result.username == user_instance.username
    assert result.email == user_instance.email
    assert result.image_url == user_instance.image_url

    # Проверяем вызовы моков
    mock_db_session.execute.assert_called()
    user_instance.one.assert_called()
    mock_db_session.commit.assert_called()


async def test_get_user_by_id_fail(mock_db_session):
    mock_db_session.execute.side_effect = NoResultFound
    result = await get_user_by_id(mock_db_session, 1000000)
    assert result is None


async def test_get_user_by_username(mock_db_session):
    # Создаем мок для результата запроса к базе данных
    user_instance = MagicMock()
    user_instance.id = 1
    user_instance.username = 'gelo21region'
    user_instance.email = 'popov.gleb.01@mail.ru'
    user_instance.image_url = None
    user_instance.one.return_value = user_instance

    # Устанавливаем моки для сессии и результата запроса
    mock_db_session.execute.return_value = user_instance
    mock_db_session.commit.return_value = None

    result = await get_user_by_username(mock_db_session, 'gelo21region')

    assert result is not None
    assert isinstance(result, UserReadRequest)
    assert result.user_id == user_instance.id
    assert result.username == user_instance.username
    assert result.email == user_instance.email
    assert result.image_url == user_instance.image_url

    mock_db_session.execute.assert_called()
    user_instance.one.assert_called()
    mock_db_session.commit.assert_called()


async def test_get_user_by_username_fail(mock_db_session):
    mock_db_session.execute.side_effect = NoResultFound
    result = await get_user_by_username(mock_db_session, 'lox')
    assert result is None


async def test_get_users_in_room(mock_db_session):
    # Создаем мок для результата запроса к базе данных
    user_data = [
        (1, 'lox', 'sample1@mail.com', None, None),
        (2, 'antilox', 'sample2@mail.com', None, None),
    ]

    mock_result = AsyncMock()
    mock_result.fetchall.return_value = user_data
    mock_db_session.execute.return_value = mock_result

    room_id = 1

    # Вызов тестируемой функции
    result = await get_users_in_room(mock_db_session, room_id)

    # Проверка результатов
    assert len(result) == 2
    assert result[0] == UserReadRequest(user_id=1, username='lox', email='sample1@mail.com', image_url=None)
    assert result[1] == UserReadRequest(user_id=2, username='antilox', email='sample2@mail.com', image_url=None)

    # Проверка вызовов
    mock_db_session.execute.assert_called_once_with(ANY)
    mock_db_session.commit.assert_called_once()


# async def test_update_user_image(mock_db_session):
#     # Создаем мок для текущего пользователя
#     current_user = UserRead(id=1, username="test_user", email="test_user@email.com", creation_date=datetime.now(),
#                             image_url=None)
#
#     # Создаем мок для файла
#     mock_file = AsyncMock(spec=UploadFile)
#
#     with patch("aws.service.upload", new_callable=AsyncMock) as mock_upload, patch("aws.service.get_url",
#                                                                                    new_callable=AsyncMock) as mock_get_url:
#         mock_upload.return_value = FileRead(file_name="test_file")
#         mock_get_url.return_value = "test_url"
#
#         result = await update_user_image(mock_db_session, current_user, mock_file)
#
#     # Проверяем, что функции upload и get_url были вызваны с правильными аргументами
#     mock_upload.assert_called_once_with(mock_file)
#     mock_get_url.assert_called_once_with("test_file")
#
#     # Проверяем, что был выполнен commit
#     mock_db_session.commit.assert_called_once()
#
#     # Проверяем, что результат соответствует ожидаемому
#     assert result == UserBaseReadRequest(user_id=current_user.id, username=current_user.username, image_url="test_url")


async def test_update_user_image_failure(mock_db_session):
    # Создаем пользователя
    current_user = UserRead(id=1, username="test_user", email="test_user@email.com", creation_date=datetime.now(),
                            image_url=None)
    # Мокаем функцию upload, чтобы она вызвала исключение
    upload_mock = AsyncMock(side_effect=Exception("Upload failed"))
    # Подготовка файла
    file = UploadFile(...)
    # Вызываем функцию для тестирования
    result = await update_user_image(mock_db_session, user, file)
    # Проверяем, что сессия была вызвана правильно
    mock_db_session.rollback.assert_called_once()
    # Проверяем, что функция вернула None
    assert result is None
