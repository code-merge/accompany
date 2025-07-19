from app.modules.onboarding.data.constants import steps
from app.modules.onboarding.utils.cookies_utils import get_user_locale, get_user_theme


def get_locale_and_theme(request):
    """
    Determines the user's language and theme preferences.

    Parameters:
    -----------
    request : Request
        FastAPI request object containing session and cookie data.

    Returns:
    --------
    tuple[str, str]
        A tuple of (language, theme), derived from:
        - `request.session["language"]` or fallback to `get_user_locale(request)`
        - `request.session["theme"]` or fallback to `get_user_theme(request)`

    Notes:
    ------
    - Prioritizes session values over cookie-based defaults.
    - Used during onboarding page rendering to personalize content.
    """
    return (
        request.session.get("language") or get_user_locale(request),
        request.session.get("theme") or get_user_theme(request),
    )


def build_context(request, current_step, extra=None):
    """
    Builds a unified rendering context for onboarding steps.

    Parameters:
    -----------
    request : Request
        FastAPI request object, includes session and headers.
    current_step : int
        The current step index in the onboarding flow.
    extra : dict | None
        Optional dictionary of additional context keys to merge.

    Returns:
    --------
    dict
        A context dictionary containing:
        - request : Request object
        - steps : list of defined onboarding steps
        - current_step : the current onboarding step index
        - locale : language preference
        - theme : theme preference
        - is_htmx : bool, indicates if request is made via HTMX
        - any additional keys from `extra`

    Notes:
    ------
    - Combines fixed context with session-derived preferences.
    - Supports HTMX rendering logic via header inspection.
    - Used across route handlers to pass data to Jinja templates.
    """
    locale, theme = get_locale_and_theme(request)
    print(locale)
    context = {
        "request": request,
        "steps": steps,
        "current_step": current_step,
        "locale": locale,
        "theme": theme,
        "is_htmx": request.headers.get("hx-request") == "true"
    }
    if extra:
        context.update(extra)
    return context