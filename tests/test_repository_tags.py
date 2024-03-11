import unittest

from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Picture, Tag, User
from src.schemas import TagModel, TagResponse
from src.repository.tags import (
    get_tags,
    get_tag,
    create_tag,
    update_tag,
    remove_tag,
    get_picture_tags,
)


class TestTags(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        #self.user = User(id=1)

    async def test_get_tags(self):
        tags =[ Tag(), Tag(), Tag() ]
        self.session.query().offset().limit().all.return_value = tags
        result = await get_tags(skip=0, limit=10, db=self.session)
        self.assertEqual(result, tags)

    async def test_get_tag_found(self):
        tag = Tag()
        self.session.query().filter().first.return_value = tag
        result = await get_tag(tag_id=1, db=self.session)
        self.assertEqual(result, tag)

    async def test_get_tag_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_tag(tag_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_create_tag(self):
         tag = TagModel(name="name")
         result = await create_tag(body=tag,  db=self.session)
         self.assertEqual(result.name, tag.name)
         self.assertTrue(hasattr(result, "id"))

    async def test_update_tag_found(self):
        tag = TagModel(name="name2")
        tag_update = Tag()
        self.session.query().filter().first.return_value = tag_update
        self.session.commit.return_value = None
        result = await update_tag(tag_id=1, body=tag, db=self.session)
        self.assertEqual(result, tag_update)

    async def test_update_contact_not_found(self):
         tag = TagModel(name="name2")
         self.session.query().filter().first.return_value = None
         self.session.commit.return_value = None
         result = await update_tag(tag_id=1, body=tag, db=self.session)
         self.assertIsNone(result)

    async def test_remove_tag_found(self):
        tag = Tag()
        self.session.query().filter().first.return_value = tag
        result = await remove_tag(tag_id=1, db=self.session)
        self.assertEqual(result, tag)


    async def test_remove_tag_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_tag(tag_id=1, db=self.session)
        self.assertIsNone(result)


    async def test_get_picture_tags_found(self):
        picture=Picture()
        tag = Tag()
        picture.tags.append(tag)
        self.session.query().filter().first.return_value = picture
        result = await get_picture_tags(picture_id=1, db=self.session)
        self.assertEqual(result, [tag])


    async def test_get_picture_tags_not_found(self):
        picture = Picture()
        picture.tags=[]
        self.session.query().filter().first.return_value = picture
        result = await get_picture_tags(picture_id=1, db=self.session)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()