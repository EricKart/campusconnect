"""
Smoke tests -- run in CI on every push and PR, before anything gets built
into a Docker image. No database or Redis needed: these check the parts of
the app that can be verified in isolation. Catching a broken import or a
password-hashing regression here is a lot cheaper than catching it after a
15-minute deploy to AKS.
"""
import pytest
from pydantic import ValidationError

from app.main import app
from app.schemas import UserCreate
from app.security import create_access_token, hash_password, verify_password


def test_app_imports_and_has_routes():
    routes = {r.path for r in app.routes}
    assert "/health" in routes
    assert "/auth/register" in routes
    assert "/posts" in routes


def test_password_hash_roundtrip():
    hashed = hash_password("correct horse battery staple")
    assert hashed != "correct horse battery staple"
    assert verify_password("correct horse battery staple", hashed)
    assert not verify_password("wrong password", hashed)


def test_jwt_round_trips_user_id():
    import jwt as pyjwt
    from app.config import settings

    token = create_access_token(user_id=42)
    payload = pyjwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    assert payload["sub"] == "42"


def test_user_create_schema_accepts_valid_data():
    user = UserCreate(
        name="Asha Rao", email="asha@campus.edu", password="Passw0rd123",
        department="CS", year=3,
    )
    assert user.email == "asha@campus.edu"


@pytest.mark.parametrize("bad_fields", [
    {"password": "short"},          # below min_length=6
    {"email": "not-an-email"},      # fails EmailStr
    {"year": 7},                    # outside ge=1, le=4
])
def test_user_create_schema_rejects_invalid_data(bad_fields):
    base = dict(name="Asha Rao", email="asha@campus.edu", password="Passw0rd123", department="CS", year=3)
    base.update(bad_fields)
    with pytest.raises(ValidationError):
        UserCreate(**base)
