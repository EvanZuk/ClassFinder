import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_css(client):
    response = client.get('/index.css')
    assert response.status_code == 200
    assert response.content_type == 'text/css; charset=utf-8' 

def test_favicon(client):
    response = client.get('/favicon.ico')
    assert response.status_code == 200
    assert response.content_type == 'image/x-icon' or response.content_type == 'image/vnd.microsoft.icon'