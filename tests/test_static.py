import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

app.config['TESTING'] = True

@pytest.fixture
def client():
    with app.test_client() as cclient:
        yield cclient

def test_index_css(client):
    response = client.get('/index.css')
    assert response.status_code == 200
    assert response.content_type == 'text/css; charset=utf-8'

def test_favicon(client):
    response = client.get('/favicon.ico')
    assert response.status_code == 200
    assert response.content_type == 'image/vnd.microsoft.icon' or response.content_type == 'image/x-icon'

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'