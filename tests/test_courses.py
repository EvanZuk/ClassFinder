import os
import sys
import pytest
from freezegun import freeze_time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from test_users import apilogin

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@freeze_time("2024-10-10 7:35")
def test_currentperiod(client):
    token = apilogin(client)
    response = client.get('/api/v1/currentperiod/', headers={'Authorization': f'pytest {token}'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'

@freeze_time("2024-10-10 7:35")
def test_currentcourses(client):
    token = apilogin(client)
    response = client.get('/api/v1/currentcourses/', headers={'Authorization': f'pytest {token}'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'

@freeze_time("2024-10-10 7:35")
def test_to_canvas(client):
    token = apilogin(client)
    response = client.get('/canvas/', headers={'Authorization': f'pytest {token}'})
    assert response.status_code == 302
    assert response.headers['Location'].startswith('https://')

@freeze_time("2024-10-10 7:35")
def test_to_canvas_modules(client):
    token = apilogin(client)
    response = client.get('/canvas/modules/', headers={'Authorization': f'pytest {token}'})
    assert response.status_code == 302
    assert response.headers['Location'].startswith('https://')

@freeze_time("2024-10-10 7:35")
def test_home(client):
    token = apilogin(client)
    response = client.get('/', headers={'Authorization': f'pytest {token}'})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

def test_courses(client):
    token = apilogin(client)
    response = client.get('/api/v1/courses/', headers={'Authorization': f'pytest {token}'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert isinstance(response.json['courses'], list)

def test_import_courses(client):
    token = apilogin(client)
    response = client.post('/bulkaddcourse/', headers={'Authorization': f'pytest {token}'}, json={'courses': "2\nMS TESTING\nTime\nTeacher\nRm: 1234", 'join': True})
    assert response.status_code == 200
    assert response.json['status'] == 'success'

