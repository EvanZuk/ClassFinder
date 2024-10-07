import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from test_users import apilogin

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_admin_createaccount(client):
    token = apilogin(client)
    # This fails when login is true so it cant be tested.
    response = client.post('/admin/createaccount/', headers={'Authorization': f'pytest {token}'}, json={'email': 'test.adminaccount@s.stemk12.org', 'username': 'adminaccount1352', 'password': 'password4123', 'login': False})
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_admin_createaccount_invalid_email(client):
    token = apilogin(client)
    response = client.post('/admin/createaccount/', headers={'Authorization': f'pytest {token}'}, json={'email': 'testnotreal@gmail.com', 'username': 'adminaccount2', 'password': 'password2'})
    assert response.status_code == 400

def test_admin_change_time(client):
    token = apilogin(client)
    response = client.post('/admin/changetimes/', headers={'Authorization': f'pytest {token}'}, json={'day': 2})
    assert response.status_code == 200
    assert response.json['status'] == 'success'