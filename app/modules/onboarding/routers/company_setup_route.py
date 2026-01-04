
from pathlib import Path
from pydantic import ValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, File, Form, Request, UploadFile

from app.core.session_manager import SessionManager
from app.core.templating.template_utils import render
from app.modules.onboarding.models.company_model import CompanyData
from app.modules.onboarding.utils.context_utils import build_context
from app.modules.onboarding.data.constants import INDUSTRIES


router = APIRouter()

ALLOWED_COMPANY_LOGOS   = {".jpg", ".jpeg", ".png", ".gif"} | {".svg"}

@router.get("/company-setup", name="company-setup", response_class=HTMLResponse)
async def company_setup(request: Request):
    """
    Handles the GET request for the company setup page during onboarding.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        HTMLResponse: The rendered company setup HTML page with context including form data, errors, languages, themes, and industry options.

    Process:
        - Retrieves the session manager for the request.
        - Gets the current form data and errors for the "company" step.
        - Removes any errors related to "company_logo".
        - Saves the updated form and errors back to the session.
        - Builds the template context with form data, errors, and additional options.
        - Renders and returns the "company_setup.html" template.
    """
    sm     = SessionManager(request)
    form   = sm.get_form("company")
    errors = sm.get_errors("company")
    errors.pop("company_logo", None)
    sm.save_form("company", form, errors)

    ctx = build_context(request, current_step=5, extra={
        "form":      form,
        "errors":    errors,
        "industry_options": INDUSTRIES
    })
    return render("company_setup.html", request, ctx)

@router.post("/company-setup")
async def company_setup_post(
    request:       Request,
    company_name:  str        = Form(...),
    industry:      str        = Form(...),
    company_logo:  UploadFile = File(None),
):
    """
    Handles the POST request for the company setup form.

    Processes form data including company name, industry, and an optional company logo file.
    Validates the input using the CompanyData model and checks the logo file extension.
    Saves form data and errors in the session manager. If there are validation errors,
    renders the company setup page with error messages. On successful validation,
    clears errors and redirects to the system setup page.

    Args:
        request (Request): The incoming HTTP request.
        company_name (str): The name of the company, submitted via form data.
        industry (str): The industry of the company, submitted via form data.
        company_logo (UploadFile, optional): The uploaded company logo file.

    Returns:
        Response: Renders the company setup page with errors if validation fails,
                otherwise redirects to the system setup page.
    """
    sm     = SessionManager(request)
    form   = {"company_name": company_name, "industry": industry}
    errors = {}

    try:
        CompanyData(company_name=company_name, industry=industry)
    except ValidationError as ve:
        err = ve.errors()[0]
        errors[err["loc"][0]] = err["msg"]

    if company_logo:
        ext = Path(company_logo.filename or "").suffix.lower()
        if ext not in ALLOWED_COMPANY_LOGOS:
            errors["company_logo"] = "Allowed: .jpg .jpeg .png .gif .svg"

    sm.save_form("company", form, errors)

    if errors:
        return render("company_setup.html", request,
                      build_context(request, current_step=5,
                                    extra={"form": form, "errors": errors}))

    sm.clear_errors("company")
    return RedirectResponse(request.url_for("system-setup"), status_code=302)
