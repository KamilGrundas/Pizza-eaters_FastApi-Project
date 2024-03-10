import pytest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from random import randint
from datetime import datetime

from src.database.models import Picture, User, Tag
from src.schemas import ContactBase
from src.repository.pictures import get_picture, get_pictures


@pytest.fixture(scope="module")
async def user_in_db(session, user):
    user_to_db = User(**user)
    session.add(user_to_db)
    session.commit()


@pytest.fixture(scope="module")
def picture():
    return {
        "url": "some_url",
        "public_id": "picture_name",
        "description": None,
        "user_id": 1,
    }


@pytest.fixture(scope="module")
def tags():
    return [{"name": "aaaa"}, {"name": "bbbbb"}, {"name": "ccccc"}]


@pytest.fixture(scope="module")
def comment():
    return [{"text": "fg6rhyryhr", "user_id": 1}]


@pytest.fixture(scope="module")
async def tags_in_db(session, tags):
    for tag in tags:
        session.add(Tag(**tag))


async def prepare_picture(session, tags, picture, comment):
    for tag in tags:
        session.add(Tag(**tag))

    session.commit()

    picture = Picture()


async def test_get_pictures(session):
    pass
