import json
from pathlib import Path
from pydantic import ValidationError
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.config.config import settings
from app.core.session_manager import SessionManager
from app.core.templating.template_utils import render
from app.modules.onboarding.data.constants import LANGUAGES, THEMES
from app.modules.onboarding.utils.context_utils import build_context
from app.modules.onboarding.models.system_info_model import SystemData


router = APIRouter()

data_file      = Path(settings.MODULE_DATA_DIRS[0]) / "data.json"
raw_countries  = json.loads(data_file.read_text(encoding="utf-8"))

COUNTRY_OPTIONS = [
    {"value": c["code"], "label": c["name"]}
    for c in raw_countries
]
CURRENCIES = sorted({c["currency"] for c in raw_countries if c.get("currency")})
TIMEZONES  = sorted({c["timezone"] for c in raw_countries if c.get("timezone")})
MODULE_LIST = ["CRM", "HR", "Accounting", "Inventory", "Sales",
               "Purchases", "Manufacturing"]

@router.get("/system-setup", name="system-setup", response_class=HTMLResponse)
async def system_setup(request: Request):
    """
    Displays the System Setup onboarding form with pre-populated session data.

    Parameters:
    -----------
    request : Request
        The FastAPI request object containing session information.

    Behavior:
    ---------
    - Retrieves the current system form and validation errors from session.
    - Ensures modules list is initialized and cleans stale module-related errors.
    - Constructs a rendering context with available form options:
        - Countries, currencies, timezones, languages, themes, module choices.
    - Renders and returns the onboarding HTML page `system_setup.html`.

    Returns:
    --------
    HTMLResponse
        The rendered HTML page displaying the system setup form.
    """
    sm     = SessionManager(request)
    form   = sm.get("system_form", {})
    errors = sm.get("system_errors", {})
    form.setdefault("modules", [])
    errors.pop("modules", None)
    sm.set("system_errors", errors)

    ctx = build_context(request, current_step=6, extra={
        "form":            form,
        "errors":          errors,
        "country_options": COUNTRY_OPTIONS,
        "currencies":      CURRENCIES,
        "timezones":       TIMEZONES,
        "languages":       LANGUAGES,
        "themes":          THEMES,
        "modules":         MODULE_LIST
    })
    return render("system_setup.html", request, ctx)

@router.post("/system-setup")
async def system_setup_post(
    request:      Request,
    country_code: str       = Form(...),
    timezone:     str       = Form(...),
    currency:     str       = Form(...),
    language:     str       = Form(...),
    theme:        str       = Form(...),
    modules:      list[str] = Form([]),
):
    """
    Handles submission of the System Setup onboarding form.

    Parameters:
    -----------
    request : Request
        The incoming request object containing session state.
    country_code : str
        Selected country code.
    timezone : str
        Selected timezone string.
    currency : str
        Selected currency string.
    language : str
        Selected language code.
    theme : str
        Selected theme name.
    modules : list[str]
        List of starter modules selected by the user.

    Behavior:
    ---------
    - Constructs a `SystemData` Pydantic model from submitted form data.
    - On validation failure:
        - Parses the first error
        - Stores errors and form data in session
        - Renders `system_setup.html` with contextual form errors.
    - On success:
        - Clears any previous errors from session
        - Stores the validated form
        - Redirects to the final onboarding step `/finish`.

    Returns:
    --------
    HTMLResponse
        If validation fails, returns the form page with errors.
    RedirectResponse
        If successful, redirects to the onboarding finish step.
    """
    sm = SessionManager(request)
    form = {
        "country_code": country_code,
        "timezone":     timezone,
        "currency":     currency,
        "language":     language,
        "theme":        theme,
        "modules":      modules
    }
    errors = {}

    try:
        SystemData(**form)
    except ValidationError as ve:
        err = ve.errors()[0]
        errors[err["loc"][0]] = err["msg"]

    sm.set("system_form", form)
    sm.set("system_errors", errors)

    if errors:
        return render("system_setup.html", request,
                      build_context(request, current_step=6,
                                    extra={
                                        "form": form, "errors": errors,
                                        "country_options": COUNTRY_OPTIONS,
                                        "currencies": CURRENCIES,
                                        "timezones": TIMEZONES,
                                        "languages": LANGUAGES,
                                        "themes": THEMES,
                                        "modules": MODULE_LIST
                                    }))

    sm.pop("system_errors", None)
    return RedirectResponse(request.url_for("finish"), status_code=302)