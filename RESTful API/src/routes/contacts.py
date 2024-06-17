from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactCreate, ContactUpdate, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
            description='No more than 5 requests per minute',
            dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def create_contact(
    contact: ContactCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(auth_service.get_current_user),
)-> ContactResponse:
    """
    Create a new contact.

    :param contact: The contact data.
    :type contact: ContactCreate
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The created contact.
    :rtype: ContactResponse
    """
    return await repository_contacts.create_contact(contact, current_user, db)

@router.get("/", response_model=List[ContactResponse],
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
)-> List[ContactResponse]:
    """
    Retrieve a list of contacts.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: A list of contacts.
    :rtype: List[ContactResponse]
    """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts

@router.get("/search", response_model=List[ContactResponse])
async def search_contacts(
    first_name: Optional[str] = Query(None, alias="first_name"),
    last_name: Optional[str] = Query(None, alias="last_name"),
    email: Optional[str] = Query(None, alias="email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),    
) -> List[ContactResponse]:
    """
    Search for contacts by first name, last name, or email.

    :param first_name: The first name to search for.
    :type first_name: Optional[str]
    :param last_name: The last name to search for.
    :type last_name: Optional[str]
    :param email: The email to search for.
    :type email: Optional[str]
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: A list of matching contacts.
    :rtype: List[ContactResponse]
    """
    return await repository_contacts.search_contacts(first_name, last_name, email, current_user, db)

@router.get("/upcoming_birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(
    db: Session = Depends(get_db), 
    current_user: User = Depends(auth_service.get_current_user),
) -> List[ContactResponse]:
    """
    Retrieve contacts with upcoming birthdays within the next week.

    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: A list of contacts with upcoming birthdays.
    :rtype: List[ContactResponse]
    """
    today = datetime.today()
    next_week = today + timedelta(days=7)
    contacts = await repository_contacts.get_contacts_with_upcoming_birthdays(today, next_week, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> ContactResponse:
    """
    Retrieve a single contact by ID.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The contact with the specified ID.
    :rtype: ContactResponse
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact: ContactUpdate, 
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> ContactResponse:
    """
    Update an existing contact by ID.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param contact: The updated contact data.
    :type contact: ContactUpdate
    :param current_user: The current authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact.
    :rtype: ContactResponse
    """
    updated_contact = await repository_contacts.update_contact(contact_id, contact, current_user, db)
    if updated_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return updated_contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
)-> ContactResponse:
    """
    Delete a contact by ID.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The deleted contact.
    :rtype: ContactResponse
    """
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
