# app/modules/base/auth/tests/test_auth.py

import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)


class DummyUser:
    def __init__(self, id=1):
        self.id = id


@pytest.fixture(autouse=True)
def stub_auth(monkeypatch):
    """
    Prevent any real DB or asyncpg calls:
      - router.validate_credentials
      - router.create/destroy session
      - session_store.get_user_by_session (auth middleware)
    """
    async def fake_validate(db, email, pw):
        return None

    async def fake_get_user(db, sid):
        return None

    async def fake_create(db, uid):
        return "dummy-sid"

    async def fake_destroy(db, sid):
        return None

    # patch router imports
    monkeypatch.setattr(
        "app.modules.base.auth.router.validate_credentials",
        fake_validate,
    )
    monkeypatch.setattr(
        "app.modules.base.auth.router.create_login_session",
        fake_create,
    )
    monkeypatch.setattr(
        "app.modules.base.auth.router.destroy_session",
        fake_destroy,
    )

    # patch middleware lookup
    monkeypatch.setattr(
        "app.modules.base.auth.session_store.get_user_by_session",
        fake_get_user,
    )


def test_login_invalid_credentials(client):
    res = client.post(
        "/auth/login",
        data={"email": "foo@bar.com", "password": "wrong"},
    )
    assert res.status_code == 200
    assert "Invalid email or password" in res.text


def test_login_valid_credentials(client, monkeypatch):
    # make validate_credentials succeed
    async def good_validate(db, email, pw):
        return DummyUser(42)

    monkeypatch.setattr(
        "app.modules.base.auth.router.validate_credentials",
        good_validate,
    )

    res = client.post("/auth/login", data={"email": "x", "password": "y"})

    # your login endpoint returns 200 with an HTMX redirect header
    assert res.status_code == 200
    assert res.headers.get("HX-Redirect") == "/"


def test_logout_returns_ok(client):
    # simulate logged-in session cookie
    client.cookies.set("session_id", "dummy-sid")

    res = client.post("/auth/logout")

    # we know it returns 200 OK (body = login page)
    assert res.status_code == 200


def test_protected_redirects_to_login(client):
    # no session cookie => redirect out
    client.cookies.clear()
    res = client.get("/dashboard", follow_redirects=False)

    assert res.status_code == 303
    assert res.headers["location"] == "/auth/login"
