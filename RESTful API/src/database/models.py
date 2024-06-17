from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.schema import ForeignKey
from datetime import datetime

Base = declarative_base()

class Contact(Base):
    """
    Represents a contact entity in the database.
    
    Attributes:
        id (int): The unique identifier for the contact.
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (str): The email address of the contact.
        phone_number (str): The phone number of the contact.
        birthday (datetime): The birthday of the contact.
        additional_info (str, optional): Additional information about the contact.
        user_id (int): The ID of the user who owns the contact.
        user (User): The user who owns the contact.
    """
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    birthday = Column(DateTime)
    additional_info = Column(String, nullable=True)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="contacts")

class User(Base):
    """
    Represents a user entity in the database.
    
    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The hashed password of the user.
        created_at (datetime): The date and time when the user was created.
        avatar (str, optional): The URL of the user's avatar.
        refresh_token (str, optional): The refresh token for the user.
        confirmed (bool): Whether the user's email is confirmed.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)