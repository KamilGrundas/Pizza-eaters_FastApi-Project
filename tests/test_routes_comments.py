from unittest.mock import MagicMock, patch

import pytest

from src.database.models import User, UserRoleEnum, Picture, Comment
from src.services import auth_new as auth_service


ADMIN_ID = 1
COMMENT_AUTHOR_ID = 2
ANOTHER_USER_ID = 3

USER_PASSWORD = "secret"
ADMIN_PASSWORD = "admin"

PICTURE_EXISTS_ID = 1
PICTURE_NOT_EXIST_ID = 2

SIGN_UP_URL = "/api/auth/signup"


def get_picture_url(num):
    return f"/wizards/pictures/{num}/comments"


@pytest.fixture()
def filled_database(session, client):

    admin_dict = {
        "username": "admin",
        "email": "admin@admin.com",
        "password": ADMIN_PASSWORD,
        # "confirmed": True,
        # "role": UserRoleEnum.ADMIN,
    }

    response = client.post(url=SIGN_UP_URL, json=admin_dict)
    # Tutaj musi odbyć się rejestracja, bo inaczej hasło jest niezahaszowane !!!
    with open("tests.txt", "w") as fh:
        print(f" admin_sign_up_response = {response.json()}", file=fh)
        print(f"response_status = {response.status_code}", file=fh)

    assert response.status_code == 201

    admin = User(**admin_dict)
    session.add(admin)
    session.commit()

    for i in range(1, 3):
        user_dict = {
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "password": USER_PASSWORD,
            "confirmed": True,
            "role": UserRoleEnum.USER,
        }

        user = User(**user_dict)
        session.add(user)
        session.commit()
        session.refresh(user)

    picture_dict = {
        "public_id": "some_name",
        "url": "some_url",
        "user_id": ANOTHER_USER_ID,
    }

    picture = Picture(**picture_dict)
    session.add(picture)
    session.commit()

    comment_dict = {
        "picture_id": 1,
        "picture_comment_id": 1,
        "text": "some comment",
        "user_id": COMMENT_AUTHOR_ID,
    }

    comment = Comment(**comment_dict)
    session.add(comment)
    session.commit()

    return session


@pytest.fixture()
def token_author_comment(client, filled_database):

    user = filled_database.query(User).filter(User.id == COMMENT_AUTHOR_ID).first()
    comment = (
        filled_database.query(Comment)
        .filter(Comment.user_id == COMMENT_AUTHOR_ID)
        .first()
    )

    assert user.role == UserRoleEnum.USER
    assert comment != None
    assert comment.picture_id == 1
    assert comment.picture_comment_id == 1

    response = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": USER_PASSWORD},
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture()
def token_another_user(client, filled_database):

    user = filled_database.query(User).filter(User.id == ANOTHER_USER_ID).first()
    comment = (
        filled_database.query(Comment)
        .filter(Comment.user_id == ANOTHER_USER_ID)
        .first()
    )

    assert user.role == UserRoleEnum.USER
    assert comment == None

    response = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": USER_PASSWORD},
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture()
def token_admin(client, filled_database):

    user = filled_database.query(User).filter(User.id == ADMIN_ID).first()
    comment = filled_database.query(Comment).filter(Comment.user_id == ADMIN_ID).first()

    assert user.role == UserRoleEnum.ADMIN
    assert comment != None

    response = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": ADMIN_PASSWORD},
    )
    data = response.json()
    return data["access_token"]


def test_add_new_comment_picture_exists(client, token_author_comment, filled_database):
    url = get_picture_url(PICTURE_EXISTS_ID)

    num_comments_before_add = filled_database.query(Comment).count()

    new_comment_text = "comment added during test"

    response = client.post(
        url=url,
        json={"text": new_comment_text},
        headers={"Authorization": f"Bearer {token_author_comment}"},
    )

    assert response.status_code == 201

    num_comments_after_add = filled_database.query(Comment).count()

    assert num_comments_after_add == num_comments_before_add + 1

    data = response.json()
