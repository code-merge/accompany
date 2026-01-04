from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.session_manager import SessionManager
from app.core.templating.template_utils import render
from app.modules.onboarding.utils.context_utils import build_context


router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def welcome(request: Request):
    """
    Renders the onboarding welcome screen.

    Parameters:
    -----------
    request : Request
        The incoming FastAPI request with session context.

    Behavior:
    ---------
    - Uses `build_context()` to inject current onboarding step.
    - Passes session and context to the `render()` function.
    - Returns the rendered `welcome.html` page.

    Returns:
    --------
    HTMLResponse
        The onboarding welcome screen HTML.
    """
    return render("welcome.html", request, build_context(request, current_step=1))

@router.get("/licence", response_class=HTMLResponse)
async def licence(request: Request, accept: str | None = None):
    """
    Displays and optionally updates licence acceptance during onboarding.

    Parameters:
    -----------
    request : Request
        The incoming FastAPI request with session context.
    accept : str | None
        Optional query string parameter. If provided (`"true"` or `"false"`),
        it updates the session to reflect acceptance.

    Behavior:
    ---------
    - Loads previously accepted state from session manager.
    - Reads the licence text from a static file.
    - Embeds acceptance status and licence content into the context.
    - Renders `licence.html` for user review and acceptance.

    Returns:
    --------
    HTMLResponse
        The licence step page with dynamic content and acceptance tracking.
    """
    sm = SessionManager(request)
    if accept is not None:
        sm.set("licence_accepted", accept.lower() == "true")

    accepted     = sm.get("licence_accepted", False)
    license_text = Path("app/modules/onboarding/static/files/licence.txt").read_text(encoding="utf-8")
    extra = {"accepted": accepted, "license_text": license_text}
    return render("licence.html", request, build_context(request, current_step=2, extra=extra))