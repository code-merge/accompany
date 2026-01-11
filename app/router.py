# This is a temp router here.

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.modules.base.auth.dependencies import require_user
from app.core.templating.template_utils import render


router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    user = getattr(request.state, "user", None)
    return render("home.html", request, {"user": user})