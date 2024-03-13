from typing import Coroutine, Any
import pytest
import unittest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from random import randint
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Picture, User, Tag
from src.repository.pictures import add_picture

from src.database.models import Base


TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# @pytest.fixture(scope="module")
def picture_dict():
    return {
        "url": "some_url",
        "public_id": "picture_name",
        "description": None,
        "author_id": 1,
    }


# @pytest.fixture(scope="module")
def tags_list_of_dict():
    return [{"name": "aaaa"}, {"name": "bbbbb"}, {"name": "ccccc"}]


# @pytest.fixture(scope="module")
def comment_dict():
    return [{"text": "fg6rhyryhr", "user_id": 1}]


def user_dict():
    return {
        "username": "deadpool",
        "email": "deadpool@example.com",
        "password": "123456789",
    }


# @pytest.fixture(scope="module")
async def prepare_database(tags_list_of_dict, user_dict, session):
    for tag in tags_list_of_dict:
        session.add(Tag(**tag))

    session.add(User(**user_dict))

    session.commit()

    return session


class TestPictures(unittest.IsolatedAsyncioTestCase):

    def asyncSetUp(self) -> Coroutine[Any, Any, None]:
        # return super().asyncSetUp()
        engine = create_engine(
            TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )
        TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        self.session = TestingSessionLocal()
