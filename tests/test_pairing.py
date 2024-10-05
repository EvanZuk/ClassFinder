import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_pairing(client):
    global pairingresponse
    pairingresponse = client.get('/api/v1/link/')
    assert pairingresponse.status_code == 200
    assert pairingresponse.json['status'] == 'success'

def test_pairing_response(client):
    test_pairing(client)
    awaituser = client.post('/api/v1/link/', json={'code': pairingresponse.json['code']})
    assert awaituser.status_code == 200
    assert awaituser.json == {'status': 'failure', 'message': 'No account linked'}

def apilogin(client):
    response = client.post('/api/v1/login/', json={'username': 'pytest', 'password': 'password'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    global token
    token = response.json['token'] if 'token' in response.json else None

def test_pairing_login(client):
    apilogin(client)
    test_pairing_response(client)
    response = client.post('/link/', json={'code': pairingresponse.json['code']}, headers={'Authorization': f'pytest {token}', 'Content-Type': 'application/json'})
    assert response.status_code == 200
    assert response.json == {'status': 'success', 'message': 'Account linked'}

def test_pairing_login_check(client):
    test_pairing_login(client)
    response = client.post('/api/v1/link/', json={'code': pairingresponse.json['code']}, headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert response.json['username'] == 'pytest'

def test_pairing_login_check_fail_500(client):
    response = client.post('/api/v1/link/', json={'code': 'notarealcode'}, headers={'Content-Type': 'application/json'})
    assert response.status_code == 500

def test_pairing_login_check_fail_400(client):
    response = client.post('/api/v1/link/', json={'code': '99999999999999999999'}, headers={'Content-Type': 'application/json'})
    assert response.status_code == 400