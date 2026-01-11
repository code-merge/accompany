import pytest
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    return asyncio.get_event_loop()