from fastapi import Request
from typing import Optional, TypeVar

DEFAULT_LOCALE = "en"
DEFAULT_THEME = "light"
T = TypeVar("T")

def get_cookie_locale(request: Request) -> str:
    """
    Retrieves the user's preferred locale from cookies.

    Parameters:
    -----------
    request : Request
        FastAPI request object containing incoming cookies.

    Returns:
    --------
    str
        The value of the 'locale' cookie, or "en" if not present.
    """
    return request.cookies.get("locale", DEFAULT_LOCALE)

def get_cookie_theme(request: Request) -> str:
    """
    Retrieves the user's preferred theme from cookies.

    Parameters:
    -----------
    request : Request
        FastAPI request object containing incoming cookies.

    Returns:
    --------
    str
        The value of the 'theme' cookie, or "light" if not present.
    """
    return request.cookies.get("theme", DEFAULT_THEME)

def get_session_value(request: Request, key: str, default: Optional[T] = None) -> Optional[T]:
    """
    Generic helper to retrieve a value from session storage.

    Parameters:
    -----------
    request : Request
        FastAPI request object containing session data.
    key : str
        The session key to retrieve.
    default : Optional[T], optional
        Fallback value if the key is not found (defaults to None).

    Returns:
    --------
    Optional[T]
        The session value associated with the given key, or default.
    """
    return request.session.get(key, default)

def get_user_locale(request: Request) -> str:
    """
    Determines the user's locale preference using session or cookies.

    Priority:
    ---------
    1. Session value: request.session["language"]
    2. Cookie fallback: request.cookies["locale"]

    Parameters:
    -----------
    request : Request
        FastAPI request object with session and cookie data.

    Returns:
    --------
    str
        The determined locale string.
    """
    return get_session_value(request, "language") or get_cookie_locale(request)

def get_user_theme(request: Request) -> str:
    """
    Determines the user's theme preference using session or cookies.

    Priority:
    ---------
    1. Session value: request.session["theme"]
    2. Cookie fallback: request.cookies["theme"]

    Parameters:
    -----------
    request : Request
        FastAPI request object with session and cookie data.

    Returns:
    --------
    str
        The determined theme string.
    """
    return get_session_value(request, "theme") or get_cookie_theme(request)
