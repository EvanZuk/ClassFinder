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

def test_ping(client):
    response = client.get('/ping/')
    assert response.status_code == 200
    assert response.json == {'status': 'success', 'message': 'Pong'}

def test_404(client):
    response = client.get('/asdfnotarealpage/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

def test_account(client):
    token = apilogin(client)
    response = client.get('/account/', headers={'Authorization': f'pytest {token}'})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

def test_admin(client):
    token = apilogin(client)
    response = client.get('/admin/', headers={'Authorization': f'pytest {token}'})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

def test_admin_createaccount_page(client):
    token = apilogin(client)
    response = client.get('/admin/createaccount/', headers={'Authorization': f'pytest {token}'})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

def test_admin_createaccount(client):
    token = apilogin(client)
    response = client.post('/admin/createaccount/', headers={'Authorization': f'pytest {token}'}, json={'email': 'test.adminaccount@s.stemk12.org', 'username': 'adminaccount', 'password': 'password', 'login': True})
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_admin_createaccount_invalid_email(client):
    token = apilogin(client)
    response = client.post('/admin/createaccount/', headers={'Authorization': f'pytest {token}'}, json={'email': 'testnotreal@gmail.com', 'username': 'adminaccount2', 'password': 'password2'})
    assert response.status_code == 400

def test_admin_change_time_page(client):
    token = apilogin(client)
    response = client.get('/admin/changetimes/', headers={'Authorization': f'pytest {token}'})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

def test_admin_change_time(client):
    token = apilogin(client)
    response = client.post('/admin/changetimes/', headers={'Authorization': f'pytest {token}'}, json={'day': 2})
    assert response.status_code == 200
    assert response.json['status'] == 'success'