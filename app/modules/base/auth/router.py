# app/core/auth/router.py

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, Response
from starlette.status import HTTP_200_OK

from app.core.db.dependency import get_db
from app.core.templating.template_utils import render
from app.modules.base.auth.services import validate_credentials
from app.modules.base.auth.session_store import create_login_session, destroy_session

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return render("login.html", request, {})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db = Depends(get_db),
):
    # 1) Validate credentials
    user = await validate_credentials(db, email, password)
    if not user:
        # return the form fragment with error (200 OK)
        return render("login.html", request, {"error": "Invalid email or password"})

    # 2) Create a session
    sid = await create_login_session(db, user.id)

    # 3) Build a clean Response with 200 OK
    response = Response(status_code=HTTP_200_OK)

    # 4) Set secure cookie
    response.set_cookie(
        key="session_id",
        value=sid,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=3600,
        path="/",
    )

    # 5) HTMX redirect to dashboard
    response.headers["HX-Redirect"] = "/"
    return response


@router.post("/logout")
async def logout(
    request: Request,
    db = Depends(get_db),
):
    # Always return a Response
    response = Response(status_code=HTTP_200_OK)

    sid = request.cookies.get("session_id")
    if sid:
        await destroy_session(db, sid)
        response.delete_cookie("session_id", path="/")

    response.headers["HX-Redirect"] = "/auth/login"
    return response
