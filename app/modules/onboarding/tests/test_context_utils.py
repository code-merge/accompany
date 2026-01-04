from fastapi import Request
from app.modules.onboarding.utils.context_utils import build_context

class DummyRequest:
    """
    A minimal request stub used to simulate a FastAPI `Request` object in unit tests.

    Attributes:
    -----------
    session : dict
        Simulated session data, typically used for theme/language configuration.
    scope : dict
        A mapping containing the session data (emulates ASGI request scope).
    url : str
        Static URL string used to satisfy context generation.
    headers : dict
        Empty header dictionary placeholder.
    cookies : dict
        Empty cookie dictionary placeholder.
    """
    def __init__(self):
        self.session = {"language": "en", "theme": "default"}
        self.scope = {"session": self.session}
        self.url = "http://test"
        self.headers = {}
        self.cookies = {}


def test_build_context_keys():
    """
    Tests that `build_context()` correctly injects the `current_step` key into the context.

    Behavior:
    ---------
    - Constructs a mock request using `DummyRequest`.
    - Calls `build_context()` with `current_step=3`.
    - Asserts that the returned context dictionary contains the `current_step` key.

    Returns:
    --------
    None
    """
    req = DummyRequest()
    ctx = build_context(req, current_step=3)
    assert "current_step" in ctx
