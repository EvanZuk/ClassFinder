import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_css(client):
    response = client.get('/indexa.css')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/css; charset=utf-8'

def test_icon(client):
    response = client.get('/icon.png')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/png'

def test_small_icon(client):
    response = client.get('/icon.small.png')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/png'

def test_favicon(client):
    response = client.get('/favicon.ico')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/x-icon'

def test_app_release(client):
    response = client.get('/app-release.apk/')
    assert response.status_code == 200