import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app


@pytest.fixture
def app():
    yield fastapi_app


@pytest.fixture
def client(app):
    return TestClient(app)
