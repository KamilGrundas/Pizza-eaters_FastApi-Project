import unittest

from sqlalchemy.orm import Session
from random import randint, choice
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Picture, User, Base, UserRoleEnum, Comment
from src.repository.comments import (
    add_comment,
    get_comments,
    get_comment,
    edit_comment,
    delete_comment,
)

from src.schemas import CommentBase


TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
PICTURES_TO_TEST_NUM = 3
AUTHOR_ID = 1
ANOTHER_USER_ID = 2

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    return db


def create_admin_dict() -> dict:
    return {
        "username": "admin",
        "email": "admin@admin.com",
        "password": "admin",
        "confirmed": True,
        "role": UserRoleEnum.ADMIN,
    }


def create_user_dict(num: int) -> dict:
    return {
        "username": f"user_{num}",
        "email": f"user_{num}@user.com",
        "password": "user",
        "confirmed": True,
    }


def create_picture_dict(num: int) -> dict:
    return {"public_id": f"picture name {num}", "url": f"www.picture_url_{num}.com"}


def add_user(db: Session, data: dict) -> User:
    user = User(**data)
    db.add(user)
    db.commit()
    db.refresh(user)

    assert isinstance(user.id, int)

    return user


def add_picture(db: Session, data: dict, user_id: int) -> Picture:
    user = db.query(User).filter(User.id == user_id).first()
    if bool(user):
        picture = Picture(**data, user_id=user_id)
        db.add(picture)
        db.commit()
        db.refresh(picture)

        assert isinstance(picture.id, int)

        return picture

    raise Exception("User doesn't exist")


def create_picture_num_comments_list(pictures_in_db_num):
    comments_of_each_num = []
    for _ in range(pictures_in_db_num):
        comments_of_each_num.append(randint(0, 3))

    print(comments_of_each_num)
    return comments_of_each_num


def create_comment_table(comments_of_each_num):

    comment_table = []
    comments_num = sum(comments_of_each_num)

    current_picture_id = 1
    comment_left = comments_of_each_num[0]
    all_comment_left = comments_num
    picture_comment_id = 1
    current_comment = 1

    while all_comment_left > 0:
        if comment_left == 0:
            comment_left = comments_of_each_num[current_picture_id]
            current_picture_id += 1
            picture_comment_id = 1
            continue

        row = (current_comment, current_picture_id, picture_comment_id)
        picture_comment_id += 1
        comment_left -= 1
        all_comment_left -= 1
        current_comment += 1
        comment_table.append(row)

    print(comment_table)
    return comment_table


def prepare_data_to_test():

    db = session()

    user = create_admin_dict()
    add_user(db, user)

    user = create_user_dict(1)
    add_user(db, user)

    pictures_in_db_num = PICTURES_TO_TEST_NUM

    for i in range(pictures_in_db_num):
        picture = create_picture_dict(i + 1)
        add_picture(db, picture, 1)

    comments_of_each_num = create_picture_num_comments_list(pictures_in_db_num)
    comment_table = create_comment_table(comments_of_each_num)

    return {
        "database": db,
        "comment_table": comment_table,
        "comments_of_each_num": comments_of_each_num,
    }


class TestComments(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(self):

        data = prepare_data_to_test()

        self.author_id = AUTHOR_ID
        self.database = data["database"]
        self.comment_body = CommentBase(text="Some text")
        self.comment_edited_body = CommentBase(text="Some edited text")
        self.comment_picture_picturecomment_table = data["comment_table"]
        self.expected_comments_num = data["comments_of_each_num"]
        self.num_of_commnets = len(self.comment_picture_picturecomment_table)
        self.one_comment_to_test_delete = choice(
            self.comment_picture_picturecomment_table
        )
        self.one_comment_to_test_edit = choice(
            self.comment_picture_picturecomment_table
        )

        print(
            f"comment_picture_picturecomment_table = {self.comment_picture_picturecomment_table}"
        )
        print(f"expected_comments_num = {self.expected_comments_num}")

    @classmethod
    def tearDownClass(self):
        self.database.close()

    def test_01_database(self):
        self.assertIsInstance(self.database, Session)

    async def add_comment_choosen_picture_id(self, picture_id):
        author_id = AUTHOR_ID

        await add_comment(
            body=self.comment_body,
            db=self.database,
            picture_id=picture_id,
            author_id=author_id,
        )

    async def check_if_valuable_comment_exists(self):
        comment_in_db = self.database.query(Comment).first()

        self.assertIsInstance(comment_in_db.picture_comment_id, int)
        self.assertEqual(comment_in_db.text, self.comment_body.text)
        self.assertIsInstance(comment_in_db.created_at, datetime)
        self.assertIsInstance(comment_in_db.edited_at, datetime)
        self.assertFalse(comment_in_db.is_deleted)

    async def check_if_picture_comment_id_is_equal_to_expected(
        self, number_of_comment, expected_picture_comment_id
    ):
        comment_in_db = (
            self.database.query(Comment).offset(number_of_comment - 1).first()
        )

        self.assertEqual(comment_in_db.picture_comment_id, expected_picture_comment_id)

    async def check_if_number_of_comments_is_equal_to_expected(
        self, expected_comment_num
    ):
        comment_num = self.database.query(Comment).count()

        self.assertEqual(comment_num, expected_comment_num)

    async def test_02_add_comments(self):

        for row in self.comment_picture_picturecomment_table:
            number_of_comment = row[0]
            self.num_of_comments = number_of_comment
            picture_id = row[1]
            picture_comment_id = row[2]

            await self.add_comment_choosen_picture_id(picture_id=picture_id)
            if number_of_comment == 1:
                await self.check_if_valuable_comment_exists()
            await self.check_if_number_of_comments_is_equal_to_expected(
                number_of_comment
            )
            await self.check_if_picture_comment_id_is_equal_to_expected(
                number_of_comment=number_of_comment,
                expected_picture_comment_id=picture_comment_id,
            )

    async def get_all_comments(self, deleted_one=(0, 0, 0)):
        pictures = self.database.query(Picture).all()

        for picture in pictures:

            expected_comments_num = self.expected_comments_num[picture.id - 1]
            if deleted_one[1] == picture.id:
                expected_comments_num -= 1

            comments = await get_comments(self.database, picture.id)

            self.assertIsInstance(comments, list)
            self.assertEqual(len(comments), expected_comments_num)

            for comment in comments:
                self.assertFalse(comment.is_deleted)

    async def test_03_get_comments_after_adding(self):
        await self.get_all_comments()

    async def test_04_get_my_comment_exists(self):

        random_comment_exists = choice(self.comment_picture_picturecomment_table)

        picture_id = random_comment_exists[1]
        picture_comment_id = random_comment_exists[2]
        author_id = AUTHOR_ID

        comment = await get_comment(
            self.database, picture_id, picture_comment_id, author_id
        )

        self.assertIsInstance(comment, Comment)
        self.assertFalse(comment.is_deleted)

    async def test_05_get_not_my_comment_exists(self):

        random_comment_exists = choice(self.comment_picture_picturecomment_table)

        picture_id = random_comment_exists[1]
        picture_comment_id = random_comment_exists[2]
        author_id = ANOTHER_USER_ID

        comment = await get_comment(
            self.database, picture_id, picture_comment_id, author_id
        )

        self.assertIsNone(comment)

    async def test_06_edit_comment(self):

        picture_id = self.one_comment_to_test_edit[1]
        picture_comment_id = self.one_comment_to_test_edit[2]
        author_id = AUTHOR_ID

        await edit_comment(
            self.comment_edited_body,
            self.database,
            picture_id,
            picture_comment_id,
            author_id,
        )

        edited_comment = (
            self.database.query(Comment)
            .filter(
                Comment.picture_id == picture_id,
                Comment.picture_comment_id == picture_comment_id,
            )
            .first()
        )
        edited_comments_num = (
            self.database.query(Comment)
            .filter(Comment.text == self.comment_edited_body.text)
            .count()
        )

        self.assertIsInstance(edited_comment, Comment)
        self.assertEqual(edited_comment.text, self.comment_edited_body.text)
        self.assertEqual(edited_comments_num, 1)

    async def test_07_delete_comment(self):

        picture_id = self.one_comment_to_test_delete[1]
        picture_comment_id = self.one_comment_to_test_delete[2]

        await delete_comment(self.database, picture_id, picture_comment_id)

        deleted_comment = (
            self.database.query(Comment)
            .filter(
                Comment.picture_id == picture_id,
                Comment.picture_comment_id == picture_comment_id,
            )
            .first()
        )

        deleted_comments_num = (
            self.database.query(Comment).filter(Comment.is_deleted == True).count()
        )

        self.assertTrue(deleted_comment.is_deleted)
        self.assertEqual(deleted_comments_num, 1)

    async def test_08_get_comments_after_deleting_one(self):
        await self.get_all_comments(deleted_one=self.one_comment_to_test_delete)

    async def test_09_delete_comment_once_again(self):

        picture_id = self.one_comment_to_test_delete[1]
        picture_comment_id = self.one_comment_to_test_delete[2]

        deleted_comment = await delete_comment(
            self.database, picture_id, picture_comment_id
        )

        deleted_comments_num = (
            self.database.query(Comment).filter(Comment.is_deleted == True).count()
        )

        self.assertIsNone(deleted_comment)
        self.assertEqual(deleted_comments_num, 1)
