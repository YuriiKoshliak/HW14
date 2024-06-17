import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    update_contact,
    delete_contact,
    get_contacts_with_upcoming_birthdays
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=3, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactCreate(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            phone_number="123456789",
            birthday=datetime(1990, 5, 15)
        )
        result = await create_contact(contact=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact_found(self):
        body = ContactUpdate(
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@example.com",
            phone_number="987654321",
            birthday=datetime(1990, 5, 15)
        )
        contact = Contact(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            phone_number="123456789",
            birthday=datetime(1990, 5, 15)
        )
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, contact=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactUpdate(
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@example.com",
            phone_number="987654321",
            birthday=datetime(1990, 5, 15)
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, contact=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_delete_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contacts_with_upcoming_birthdays(self):
        today = datetime.now()
        next_week = today + timedelta(days=7)
        contacts = [Contact(birthday=today + timedelta(days=3))]
        self.session.query().filter().all.return_value = contacts

        result = await get_contacts_with_upcoming_birthdays(today=today, next_week=next_week, user=self.user, db=self.session)
        self.assertEqual(result, contacts)


if __name__ == '__main__':
    unittest.main()
