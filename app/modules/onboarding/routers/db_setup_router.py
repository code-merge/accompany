import os
import uuid
from typing import Any
from pathlib import Path
from pydantic import ValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, File, Form, Request, UploadFile

from app.core.session_manager import SessionManager
from app.modules.onboarding.utils.context_utils import build_context
from app.core.templating.template_utils import render, render_to_string
from app.modules.onboarding.models.db_model import CustomDBData, StandardDBData

router = APIRouter()

ALLOWED_CUSTOM_CERT_EXT = ".pem"


def _build_db_tabs(request: Request) -> list[dict[str, Any]]:
    """
    Builds a list of dictionaries representing database setup tabs for the onboarding process.

    Each tab contains a label, a URL for navigation, and rendered HTML content for the tab.
    The function prepares context data for both "Standard" and "Custom" database setup forms,
    including form data and validation errors, and renders the corresponding HTML templates.

    Args:
        request (Request): The current HTTP request object.

    Returns:
        list[dict[str, Any]]: A list of dictionaries, each representing a tab with its label, URL, and rendered content.
    """
    sm = SessionManager(request)
    base_ctx = build_context(request, current_step=3)

    std_ctx = {**base_ctx, "form": sm.get_form("dbsetup_standard"), "errors": sm.get_errors("dbsetup_standard")}
    cus_ctx = {**base_ctx, "form": sm.get_form("dbsetup_custom"),   "errors": sm.get_errors("dbsetup_custom")}

    return [
        {"label": "onboarding_db_type_std", "url": request.url_for("dbsetup_standard"),
         "content": render_to_string("components/db_standard.html", request, std_ctx)},
        {"label": "onboarding_db_type_custom",   "url": request.url_for("dbsetup_custom"),
         "content": render_to_string("components/db_custom.html", request, cus_ctx)},
    ]

@router.get("/db-setup", name="dbsetup", response_class=HTMLResponse)
async def dbsetup(request: Request):
    ctx = build_context(request, current_step=3, extra={
        "tab_list": _build_db_tabs(request),
        "selected": 0
    })
    return render("dbsetup.html", request, ctx)


# Standard DB Routes

@router.get("/db-setup/standard", name="dbsetup_standard", response_class=HTMLResponse)
async def dbsetup_standard(request: Request):
    """
    Handles GET requests to the '/db-setup' endpoint.

    Renders the 'dbsetup.html' template with the appropriate context for the database setup step in the onboarding process.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        HTMLResponse: The rendered HTML page for the database setup step.
    """
    sm = SessionManager(request)
    ctx = build_context(request, current_step=3, extra={
        "form": sm.get_form("dbsetup_standard"),
        "errors": sm.get_errors("dbsetup_standard")
    })
    return render("components/db_standard.html", request, ctx)

@router.post("/db-setup/standard")
async def dbsetup_standard_post(request: Request, db_name: str = Form(...)):
    """
    Handles POST requests to the "/db-setup/standard" endpoint for setting up a standard database.

    Args:
        request (Request): The incoming HTTP request object.
        db_name (str, Form): The name of the database, submitted via form data.

    Process:
        - Initializes a session manager for the request.
        - Validates the provided database name using the StandardDBData model.
        - If validation fails, captures and stores the error message.
        - Saves the form data and any errors in the session.
        - Sets the database type in the session to "standard".
        - If there are validation errors, re-renders the form with error messages.
        - If validation succeeds, clears any previous errors and redirects to the admin user setup page.

    Returns:
        - If validation errors exist: Renders the "components/db_standard.html" template with form data and errors.
        - If validation succeeds: Redirects to the "admin-user-setup" page.
    """
    sm = SessionManager(request)
    form   = {"db_name": db_name}
    errors = {}

    try:
        StandardDBData(db_name=db_name)
    except ValidationError as ve:
        errors["db_name"] = ve.errors()[0]["msg"]

    sm.save_form("dbsetup_standard", form, errors)
    sm.set("db_type", "standard")

    if errors:
        return render("components/db_standard.html", request,
                      build_context(request, current_step=3, extra={"form": form, "errors": errors}))

    sm.clear_errors("dbsetup_standard")
    return RedirectResponse(request.url_for("admin-user-setup"), status_code=302)


# Custom DB Routes

@router.get("/db-setup/custom", name="dbsetup_custom", response_class=HTMLResponse)
async def dbsetup_custom(request: Request):
    """
    Handles GET requests to the '/db-setup/custom' endpoint.

    Renders the custom database setup page as an HTML response. Retrieves the current session's form data and errors
    for the 'dbsetup_custom' step, builds the template context, and renders the 'components/db_custom.html' template.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        HTMLResponse: The rendered HTML page for the custom database setup.
    """
    sm = SessionManager(request)
    ctx = {
        **build_context(request, current_step=3),
        "form":   sm.get_form("dbsetup_custom"),
        "errors": sm.get_errors("dbsetup_custom"),
    }
    return render("components/db_custom.html", request, ctx)


@router.post("/db-setup/custom")
async def dbsetup_custom_post(
    request:  Request,
    db_name:  str        = Form(...),
    host:     str        = Form(...),
    port:     int        = Form(...),
    user:     str        = Form(...),
    password: str        = Form(...),
    ssl:      bool       = Form(False),
    ssl_cert: UploadFile = File(None),
):
    """
    Handle POST requests for custom database setup.

    This endpoint processes form data for setting up a custom database connection,
    including optional SSL certificate upload. It performs the following steps:
    1. Validates input data using Pydantic.
    2. Checks SSL certificate requirements if SSL is enabled.
    3. Persists the uploaded PEM certificate file securely and stores its path in the session.
    4. Saves the form data and any validation errors in the session.
    5. If there are errors, re-renders the form with error messages.
    6. On success, clears errors and redirects to the admin user setup step.

    Args:
        request (Request): The incoming HTTP request.
        db_name (str): Name of the database.
        host (str): Database host address.
        port (int): Database port number.
        user (str): Database username.
        password (str): Database password.
        ssl (bool, optional): Whether to use SSL. Defaults to False.
        ssl_cert (UploadFile, optional): Uploaded SSL certificate file (.pem). Defaults to None.

    Returns:
        Response: Renders the form with errors if validation fails, or redirects to the next setup step on success.
    """
    sm = SessionManager(request)

    form = {
        "db_name":  db_name,
        "host":     host,
        "port":     port,
        "user":     user,
        "password": password,
        "ssl":      ssl,
    }
    # explicitly type errors as str->str
    errors: dict[str, str] = {}

    # 1) Pydantic validation
    try:
        CustomDBData(**form)
    except ValidationError as ve:
        for err in ve.errors():
            # cast loc to str so mypy is happy
            loc0 = err["loc"][0]
            key = loc0 if isinstance(loc0, str) else str(loc0)
            errors[key] = err["msg"]

    # 2) SSL certificate checks
    if ssl:
        if not ssl_cert:
            errors["ssl_cert"] = "When SSL is on, upload a .pem file."
        else:
            ext = Path(ssl_cert.filename or "").suffix.lower()
            if ext != ALLOWED_CUSTOM_CERT_EXT:
                errors["ssl_cert"] = f"Only {ALLOWED_CUSTOM_CERT_EXT} files allowed."

    # 3) Persist PEM and stash its path in session
    if ssl and not errors.get("ssl_cert") and ssl_cert:
        cert_dir = Path.home() / ".accompany" / "certs"
        cert_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

        pem_name = f"{db_name}-{uuid.uuid4().hex}{ALLOWED_CUSTOM_CERT_EXT}"
        pem_path = cert_dir / pem_name

        contents = await ssl_cert.read()
        pem_path.write_bytes(contents)
        os.chmod(pem_path, 0o600)

        sm.set("ssl_cert_path", str(pem_path))
        form["ssl_cert_path"] = str(pem_path)

    # 4) Save form + errors + mark as custom
    sm.save_form("dbsetup_custom", form, errors)
    sm.set("db_type", "custom")

    # 5) On errors, re-render same form
    if errors:
        ctx = build_context(request, current_step=3, extra={"form": form, "errors": errors})
        return render("components/db_custom.html", request, ctx)

    # 6) Clear and proceed
    sm.clear_errors("dbsetup_custom")
    return RedirectResponse(request.url_for("admin-user-setup"), status_code=302)
