import pytest
import sys
import freezegun
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

app.config['TESTING'] = True

@pytest.fixture(scope="session")
def client():
    with app.test_client() as cclient:
        yield cclient

@pytest.fixture(scope="session")
def admintoken(client): # Simulates the first registration
    print("Creating user")
    response = client.post("/register", json={"email": "admin.pytest@s.stemk12.org"})
    assert response.status_code == 200
    assert response.json.get('emailid')
    emailid = response.json.get('emailid')
    response = client.post(f"/register/{emailid}", json={"username": "admin", "password": "password123"})
    assert response.status_code == 400
    response = client.post(f"/register/{emailid}", json={"username": "pytrwy", "password": "password123"})
    assert response.status_code == 200
    assert response.json.get('token')
    ntoken = response.json.get('token')
    assert ntoken
    yield ntoken


@pytest.fixture(scope="session")
def token(client): # Simulates a users first login and actions
    print("Creating user")
    response = client.post("/register", json={"email": "a.a@s.stemk12.org"})
    assert response.status_code == 200
    assert response.json.get('emailid')
    emailid = response.json.get('emailid')
    response = client.post(f"/register/{emailid}", json={"username": "admin", "password": "password123"})
    assert response.status_code == 400
    response = client.post(f"/register/{emailid}", json={"username": "pytrwy", "password": "password123"})
    assert response.status_code == 400
    response = client.post(f"/register/{emailid}", json={"username": "pytest", "password": "password123"})
    assert response.status_code == 200
    assert response.json.get('token')
    ntoken = response.json.get('token')
    assert ntoken
    yield ntoken

def test_dashboard_no_token(client):
    response = client.get("/dashboard", follow_redirects=False, headers={"Authorization": ""})
    assert response.status_code == 302
    assert response.location == "/login"

def test_export_data_admin(client, admintoken):
    response = client.get("/export", headers={"Authorization": f"Bearer {admintoken}"})
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.json.get('status') == "success"
    assert response.json.get('username') == "pytrwy"
    assert response.json.get('email') == "admin.pytest@s.stemk12.org"
    assert response.json.get('role') == "admin"
    assert response.json.get('classes') == []
    assert len(response.json.get('sessions')) == 1

def test_export_data(client, token):
    response = client.get("/export", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.json.get('status') == "success"
    assert response.json.get('username') == "pytest"
    assert response.json.get('email') == "a.a@s.stemk12.org"
    assert response.json.get('role') == "user"
    assert response.json.get('classes') == []
    assert len(response.json.get('sessions')) == 1

# I cant get basic authentication to be testable.

def test_dashboard_legacy_auth(client, token):
    response = client.get("/dashboard", headers={"Authorization": f"pytest {token}"})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'

def test_dashboard_invalid_legacy_auth(client):
    response = client.get("/dashboard", headers={"Authorization": "pytest invalidtoken"})
    assert response.status_code == 302 or response.status_code == 400

def test_dashboard(client, token):
    response = client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'

def test_dashboard_invalid_token(client):
    response = client.get("/dashboard", headers={"Authorization": "Bearer invalidtoken"}, follow_redirects=False)
    assert response.status_code == 302
    assert response.location == "/login"

def test_account(client, token):
    response = client.get("/account", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'