from unittest.mock import MagicMock
from src.database.models import User

TEST_EMAIL = "yuriikos@meta.ua"

def test_login_user_not_confirmed_email(client, user, session):
    user["email"] = TEST_EMAIL
    new_user = User(username=user["username"], email=user["email"], password=user["password"], confirmed=False)
    session.add(new_user)
    session.commit()

    response = client.post(
        "/api/auth/login", data={"username": user.get("email"), "password": user.get("password")})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == "Email not confirmed"

    session.delete(new_user)
    session.commit()

def test_create_user(client, user, monkeypatch):
    user["email"] = TEST_EMAIL
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["user"]["email"] == user.get("email")
    assert payload["detail"] == "User successfully created. Check your email for confirmation."
    mock_send_email.assert_called_once()


def test_repeat_create_user(client, user, monkeypatch):
    user["email"] = TEST_EMAIL
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 409, response.text
    payload = response.json()
    assert payload["detail"] == "Account already exists"


def test_login_user(client, user, session):
    user["email"] = TEST_EMAIL
    current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["token_type"] == "bearer"


def test_login_user_with_wrong_password(client, user, session):
    user["email"] = TEST_EMAIL
    current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login", data={"username": user.get("email"), "password": "password"}
    )
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == "Invalid password"


def test_login_user_with_wrong_email(client, user, session):
    user["email"] = TEST_EMAIL
    current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": "example@test.com",
              "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == "Invalid email"
