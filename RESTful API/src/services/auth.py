from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.conf.config import settings

"""
Module providing authentication services.

Attributes:
    ALGORITHM (str): The algorithm used for JWT encoding. :noindex:
    SECRET_KEY (str): The secret key used for JWT encoding. :noindex:
    pwd_context (CryptContext): The password context for hashing and verifying passwords. :noindex:
    oauth2_scheme (OAuth2PasswordBearer): The OAuth2 scheme for password-based authentication. :noindex:
"""

class Auth:
    """
    Authentication and authorization service.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
   

    def verify_password(self, plain_password, hashed_password) -> bool:
        """
        Verify if the provided plain password matches the hashed password.

        :param plain_password: The plain text password.
        :type plain_password: str
        :param hashed_password: The hashed password.
        :type hashed_password: str
        :return: True if the password matches, False otherwise.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Hash the provided password.

        :param password: The plain text password.
        :type password: str
        :return: The hashed password.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Generate a new access token.

        :param data: The data to encode in the token.
        :type data: dict
        :param expires_delta: Optional expiration time in seconds.
        :type expires_delta: Optional[float]
        :return: The encoded access token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire =  datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire =  datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"iat":  datetime.now(timezone.utc), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token


    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Generate a new refresh token.

        :param data: The data to encode in the token.
        :type data: dict
        :param expires_delta: Optional expiration time in seconds.
        :type expires_delta: Optional[float]
        :return: The encoded refresh token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire =  datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire =  datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update({"iat":  datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token
    
    def create_email_token(self, data: dict) -> str:
        """
        Generate a new email confirmation token.

        :param data: The data to encode in the token.
        :type data: dict
        :return: The encoded email token.
        :rtype: str
        """
        to_encode = data.copy()
        expire =  datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update({"iat":  datetime.now(timezone.utc), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Decode a refresh token and extract the email.

        :param refresh_token: The refresh token to decode.
        :type refresh_token: str
        :return: The email extracted from the token.
        :rtype: str
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
        """
        Retrieve the current authenticated user.

        :param token: The JWT token.
        :type token: str
        :param db: The database session.
        :type db: Session
        :return: The authenticated user.
        :rtype: User
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user
    
    async def get_email_from_token(self, token: str) -> str:
        """
        Extract email from a token.

        :param token: The token to decode.
        :type token: str
        :return: The email extracted from the token.
        :rtype: str
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                          detail="Invalid token for email verification")


auth_service = Auth()
