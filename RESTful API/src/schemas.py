from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class ContactBase(BaseModel):
    """
    Base schema for Contact.

    Attributes:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (EmailStr): The email address of the contact.
        phone_number (str): The phone number of the contact.
        birthday (datetime): The birthday of the contact.
        additional_info (Optional[str]): Any additional information about the contact.
    """
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone_number: str = Field(max_length=20)
    birthday: datetime
    additional_info: Optional[str] = None

class ContactCreate(ContactBase):
    """
    Schema for creating a new contact. Inherits all attributes from ContactBase.
    """
    pass

class ContactUpdate(ContactBase):
    """
    Schema for updating an existing contact. Inherits all attributes from ContactBase.
    """    
    pass

class ContactResponse(ContactBase):
    """
    Schema for returning contact information, including the contact ID.

    Attributes:
        id (int): The unique identifier of the contact.
    """
    id: int

    class Config:
        from_attributes = True
        

class UserModel(BaseModel):
    """
    Schema for user registration.

    Attributes:
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The password of the user.
    """
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    """
    Schema for returning user information.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        created_at (datetime): The creation time of the user record.
        avatar (str): The avatar URL of the user.
    """
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """
    Schema for returning user information after successful registration.

    Attributes:
        user (UserDb): The user information.
        detail (str): The detail message.
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    Schema for returning JWT tokens.

    Attributes:
        access_token (str): The access token.
        refresh_token (str): The refresh token.
        token_type (str): The type of the token, default is 'bearer'.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Schema for requesting email verification.

    Attributes:
        email (EmailStr): The email address to be verified.
    """
    email: EmailStr