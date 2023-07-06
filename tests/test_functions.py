import pytest
from flask import session, url_for
from app import create_app


@pytest.fixture
def app():
    app = create_app("sqlite:///:memory:")
    app.testing = True
    with app.test_client() as client:
        with app.app_context():
            yield app

@pytest.mark.skip(reason="WORK IN PROGRESS")
def test_base_redirects_to_login(app):
    with app.test_client() as client:
        response = client.get(url_for("loginUser"))
        assert response.status_code == 302
        assert response.location == url_for("loginUser", _external=True)

@pytest.mark.skip(reason="WORK IN PROGRESS")
def test_register_user(app):
    client = app.test_client()
    response = client.post(
        "/register_user",
        data={"username": "testuser", "pwd": "password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registration successful" in response.data

@pytest.mark.skip(reason="WORK IN PROGRESS")
def test_login_user(app):
    client = app.test_client()
    response = client.post(
        "/login_user",
        data={"username": "testuser", "pwd": "password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome, testuser!" in response.data
    assert session["access_token"] is not None

@pytest.mark.skip(reason="WORK IN PROGRESS")
def test_dashboard_authenticated(app):
    client = app.test_client()
    client.post(
        "/login_user",
        data={"username": "testuser", "pwd": "password"},
        follow_redirects=True,
    )

    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Logout" in response.data

@pytest.mark.skip(reason="WORK IN PROGRESS")
def test_dashboard_unauthenticated(app):
    client = app.test_client()
    response = client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"Register" in response.data

@pytest.mark.skip(reason="WORK IN PROGRESS")
def test_logout(app):
    client = app.test_client()
    client.post(
        "/login_user",
        data={"username": "testuser", "pwd": "password"},
        follow_redirects=True,
    )

    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"Register" in response.data
    assert "access_token" not in session
