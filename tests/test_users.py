import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def apilogin(client):
    response = client.post('/api/v1/login/', json={'username': 'pytest', 'password': 'password'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    global token
    token = response.json['token'] if 'token' in response.json else None
    return token

def test_signup(client):
    response = client.post('/signup/', json={'email': 'test.email@s.stemk12.org'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    return response.json['emailid']

def test_signup_invalid_email(client):
    response = client.post('/signup/', json={'email': 'testemail@gmail.com'})
    assert response.status_code == 400

def test_signup_stage_2_fail(client):
    emailid = test_signup(client)
    response = client.post('/signup/' + emailid, json={'username': 'pytest', 'password': 'password'})
    assert response.status_code == 400

def test_signup_stage_2(client):
    emailid = test_signup(client)
    response = client.post('/signup/' + emailid, json={'username': 'newaccount', 'password': 'password'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def newaccount_login(client):
    response = client.post('/api/v1/login/', json={'username': 'newaccount', 'password': 'password'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    global token
    token = response.json['token'] if 'token' in response.json else None
    return token

def change_password(client):
    token = newaccount_login(client)
    response = client.post('/api/v1/change-password/', json={'password': 'password'}, headers={'Authorization': f'newaccount {token}'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    return response.json['token']

def test_account_cycle(client):
    token = change_password(client)
    response = client.delete('/api/v1/deleteaccount/', headers={'Authorization': f'newaccount {token}'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'