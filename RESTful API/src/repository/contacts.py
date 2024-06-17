from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate

async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Optional[Contact]:
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype: Optional[Contact]
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

async def create_contact(contact: ContactCreate, user: User, db: Session) -> Contact:
    """
    Creates a new contact for a specific user.

    :param contact: The data for the contact to create.
    :type contact: ContactCreate
    :param user: The user to create the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact
    """
    db_contact = Contact(**contact.model_dump(), user_id=user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

async def update_contact(contact_id: int, contact: ContactUpdate, user: User, db: Session) -> Optional[Contact]:
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param contact: The updated data for the contact.
    :type contact: ContactUpdate
    :param user: The user to update the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None if it does not exist.
    :rtype: Optional[Contact]
    """
    db_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if db_contact:
        for key, value in contact.model_dump().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
        return db_contact
    return None

async def delete_contact(contact_id: int, user: User, db: Session) -> Optional[Contact]:
    """
    Deletes a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param user: The user to delete the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The deleted contact, or None if it does not exist.
    :rtype: Optional[Contact]
    """
    db_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
        return db_contact
    return None

async def search_contacts(first_name: Optional[str], last_name: Optional[str], email: Optional[str], user: User, db: Session) -> List[Contact]:
    """
    Searches for contacts based on the given criteria for a specific user.

    :param first_name: The first name to search for.
    :type first_name: Optional[str]
    :param last_name: The last name to search for.
    :type last_name: Optional[str]
    :param email: The email to search for.
    :type email: Optional[str]
    :param user: The user to search contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts that match the search criteria.
    :rtype: List[Contact]
    """
    query = db.query(Contact).filter(Contact.user_id == user.id)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.all()

async def get_contacts_with_upcoming_birthdays(today: datetime, next_week: datetime, user: User, db: Session) -> List[Contact]:
    """
    Retrieves contacts with birthdays within the specified date range for a specific user.

    :param today: The current date.
    :type today: datetime
    :param next_week: The date one week from today.
    :type next_week: datetime
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts with birthdays within the specified date range.
    :rtype: List[Contact]
    """
    today_str = today.strftime('%m-%d')
    next_week_str = next_week.strftime('%m-%d')

    contacts = db.query(Contact).filter(
        Contact.user_id == user.id,
        Contact.birthday.isnot(None)
    ).all()

    upcoming_birthdays = []
    for contact in contacts:
        birthday_str = contact.birthday.strftime('%m-%d')
        if today_str <= birthday_str <= next_week_str:
            upcoming_birthdays.append(contact)

    return upcoming_birthdays