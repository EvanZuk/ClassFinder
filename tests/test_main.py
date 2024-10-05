import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

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