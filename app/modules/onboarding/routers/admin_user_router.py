from pathlib import Path
from pydantic import ValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, File, Form, Request, UploadFile

from app.core.session_manager import SessionManager
from app.core.templating.template_utils import render
from app.modules.onboarding.models.admin_user_model import AdminData
from app.modules.onboarding.utils.context_utils import build_context


router = APIRouter()

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif"}


@router.get("/admin-user-setup", name="admin-user-setup", response_class=HTMLResponse)
async def admin_user_setup(request: Request):
    """
    Handles the GET request for the admin user setup page.

    This endpoint prepares the context for rendering the admin user setup form,
    including retrieving and updating error messages from the session manager,
    removing any 'profile_picture' errors, and passing the form data and errors
    to the template renderer.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        HTMLResponse: The rendered HTML page for admin user setup.
    """
    sm = SessionManager(request)
    errors = sm.get_errors("admin")
    errors.pop("profile_picture", None)
    sm.set("admin_errors", errors)
    ctx = build_context(request, current_step=4, extra={
        "form": sm.get_form("admin"),
        "errors": errors
    })
    return render("admin_user_setup.html", request, ctx)

@router.post("/admin-user-setup")
async def admin_user_setup_post(
    request:          Request,
    full_name:        str        = Form(...),
    email:            str        = Form(...),
    password:         str        = Form(...),
    confirm_password: str        = Form(...),
    profile_picture:  UploadFile = File(None),
):
    """
    Handles the POST request for the admin user setup form.

    Validates the submitted form data for creating an admin user, including full name, email, password, password confirmation, and optional profile picture. 
    Performs the following validations:
    - Checks if the full name and email are valid using the AdminData schema.
    - Ensures the password is at least 8 characters long.
    - Confirms that the password and confirm_password fields match.
    - Validates the profile picture file extension if provided.

    Saves form data and errors in the session. If there are validation errors, re-renders the setup form with error messages. 
    On successful validation, stores the admin password in the session and redirects to the company setup page.

    Args:
        request (Request): The incoming HTTP request.
        full_name (str): The full name of the admin user.
        email (str): The email address of the admin user.
        password (str): The password for the admin user.
        confirm_password (str): The password confirmation.
        profile_picture (UploadFile, optional): The profile picture file.

    Returns:
        Response: Renders the setup form with errors if validation fails, or redirects to the company setup page on success.
    """
    sm     = SessionManager(request)
    form   = {"full_name": full_name, "email": email}
    errors = {}

    try:
        AdminData(full_name=full_name, email=email)
    except ValidationError as ve:
        err = ve.errors()[0]
        errors[err["loc"][0]] = err["msg"]

    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."
    if password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."
    if profile_picture:
        ext = Path(profile_picture.filename or "").suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTS:
            errors["profile_picture"] = "Allowed: .jpg .jpeg .png .gif"

    sm.save_form("admin", form, errors)
    if errors:
        return render("admin_user_setup.html", request,
                      build_context(request, current_step=4,
                                    extra={"form": form, "errors": errors}))

    sm.set("__admin_pw", password)
    sm.clear_errors("admin")
    return RedirectResponse(request.url_for("company-setup"), status_code=302)
