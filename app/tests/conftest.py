import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    return asyncio.get_event_loop()
