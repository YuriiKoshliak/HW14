import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email_found(self):
        user = User(email="test@example.com")
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email="test@example.com", db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email="test@example.com", db=self.session)
        self.assertIsNone(result)

    @patch('src.repository.users.Gravatar')
    async def test_create_user(self, mock_gravatar):
        mock_gravatar.return_value.get_image.return_value = "avatar_url"
        
        body = UserModel(username="testuser", email="test@example.com", password="password")
        new_user = User(username="testuser", email="test@example.com", avatar="avatar_url")
        
        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = None
        
        result = await create_user(body=body, db=self.session)
        
        self.assertEqual(result.username, new_user.username)
        self.assertEqual(result.email, new_user.email)
        self.assertEqual(result.avatar, new_user.avatar)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        user = User(username="testuser", email="test@example.com", password="password", refresh_token=None)
        await update_token(user=user, token="new_token", db=self.session)
        self.assertEqual(user.refresh_token, "new_token")
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        user = User(username="testuser", email="test@example.com", password="password", confirmed=False)
        self.session.query().filter().first.return_value = user
        await confirmed_email(email="test@example.com", db=self.session)
        self.assertTrue(user.confirmed)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        user = User(username="testuser", email="test@example.com", password="password", avatar="old_avatar_url")
        self.session.query().filter().first.return_value = user
        new_avatar_url = "new_avatar_url"
        result = await update_avatar(email="test@example.com", url=new_avatar_url, db=self.session)
        self.assertEqual(result.avatar, new_avatar_url)
        self.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
