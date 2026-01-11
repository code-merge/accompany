# app/core/templating/template_utils.py

from pathlib import Path
from typing import Optional, Dict

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from jinja2 import (
    Environment,
    PrefixLoader,
    FileSystemLoader,
    TemplateNotFound,
)

from app.core.config.config import settings
from app.core.i18n.locale import get_translations


def get_loader_mapping() -> Dict[str, FileSystemLoader]:
    """
    Prefix 'core' → app/core/ui
           'modules' → app/modules
    """
    return {
        "core":    FileSystemLoader(str(settings.CORE_DIR / "ui")),
        "modules": FileSystemLoader(str(settings.MODULES_DIR)),
    }


# Create a Jinja env with PrefixLoader
env = Environment(
    loader=PrefixLoader(get_loader_mapping(), delimiter="/"),
    autoescape=True
)
env.globals["_"] = lambda s: s
templates = Jinja2Templates(env=env)


def resolve(name: str) -> str:
    """
    Turn a bare name like 'home.html' into:
      - 'core/templates/home.html' if it lives under core/ui/templates
      - 'modules/<mod>/ui/templates/<name>' for feature modules
      - 'modules/base/<submod>/ui/templates/<name>' for base submodules

    If `name` already contains '/', return it unchanged.
    """
    if "/" in name:
        return name

    # 1) core/ui/templates
    p = settings.CORE_DIR / "ui" / "templates" / name
    if p.exists():
        return f"core/templates/{name}"

    # 2) each enabled module
    for mod in settings.ENABLED_MODULES:
        p = settings.MODULES_DIR / mod / "ui" / "templates" / name
        if p.exists():
            return f"modules/{mod}/ui/templates/{name}"

    # 3) nested base submodules
    base_root = settings.MODULES_DIR / "base"
    if base_root.exists():
        for sub in base_root.iterdir():
            p = sub / "ui" / "templates" / name
            if p.exists():
                return f"modules/base/{sub.name}/ui/templates/{name}"

    raise TemplateNotFound(name)


def guess_base_template(name: str) -> Optional[str]:
    """
    Wrap fragments in the correct shell layout:
      - core → no auto-wrap (use its own {% extends ... %})
      - modules/onboarding → 'modules/onboarding/ui/templates/onboarding_base.html'
      - modules/base/auth  → 'modules/base/auth/ui/templates/auth_base.html'
    """
    full = resolve(name)
    parts = full.split("/")

    if parts[0] == "core":
        return None

    # modules/... 
    # modules/base/<sub>/...
    if parts[1] == "base":
        sub = parts[2]
        return f"modules/base/{sub}/ui/templates/{sub}_base.html"

    # modules/<mod>/...
    mod = parts[1]
    return f"modules/{mod}/ui/templates/{mod}_base.html"


def apply_module_locale(env: Environment, name: str, request: Request):
    """
    Loads i18n for whichever module (or core) the template lives in.
    """
    locale = request.cookies.get("locale", "en")
    try:
        full = resolve(name)
    except TemplateNotFound:
        env.globals["_"] = lambda s: s
        return

    parts = full.split("/")
    if parts[0] == "core":
        root = settings.CORE_DIR / "i18n"
    else:
        # modules/base/<sub> or modules/<mod>
        if parts[1] == "base":
            sub = parts[2]
            root = settings.MODULES_DIR / "base" / sub / "i18n"
        else:
            root = settings.MODULES_DIR / parts[1] / "i18n"
    
    env.globals["_"] = get_translations(root, locale)


def render(template_name: str, request: Request, context: dict) -> HTMLResponse:
    context["request"] = request
    apply_module_locale(env, template_name, request)

    tpl = resolve(template_name)

    # HTMX fragment → return raw fragment
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(tpl, context)

    # Prevent direct rendering of a base layout
    if tpl.endswith("_base.html"):
        raise ValueError(f"Refusing to render base layout directly: {tpl}")

    # Wrap in module shell if needed
    base = guess_base_template(template_name)
    if base:
        context["content_template"] = tpl
        return templates.TemplateResponse(base, context)

    # Otherwise render as-is (core pages)
    return templates.TemplateResponse(tpl, context)


def render_to_string(template_name: str, request: Request, context: dict) -> str:
    context["request"] = request
    apply_module_locale(env, template_name, request)
    tpl = resolve(template_name)
    return templates.get_template(tpl).render(context)
