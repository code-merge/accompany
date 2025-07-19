# app/core/templating/template_utils.py

from pathlib import Path
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, ChoiceLoader, FileSystemLoader

from app.core.config.config import settings
from app.core.i18n.locale import get_translations

# ─────────────────────────────────────────────────────────────────────────────
# Jinja Environment Setup
# ─────────────────────────────────────────────────────────────────────────────

def create_jinja_environment(template_dirs: list[Path]) -> Environment:
    """
    Creates and configures a Jinja2 Environment with the specified template directories.

    Args:
        template_dirs (list[Path]): A list of Path objects representing directories to search for templates.

    Returns:
        Environment: A configured Jinja2 Environment instance with a ChoiceLoader for the provided directories and a default no-op translation function.

    Note:
        The environment is set to autoescape by default, and the global '_' is set as a no-operation translation function.
    """
    loaders = [FileSystemLoader(str(p)) for p in template_dirs]
    env = Environment(loader=ChoiceLoader(loaders), autoescape=True)
    env.globals["_"] = lambda s: s  # Default noop translation
    return env

env = create_jinja_environment(settings.TEMPLATE_DIRS)
templates = Jinja2Templates(env=env)

# ─────────────────────────────────────────────────────────────────────────────
# i18n Injection (module-aware)
# ─────────────────────────────────────────────────────────────────────────────

def apply_module_locale(env: Environment, template_path: str, request: Request):
    """
    Configures the Jinja2 environment with locale-specific translations for a given template.

    This function determines the appropriate translation function based on the template's
    location (module or core) and the user's locale (from cookies). It sets the translation
    function as the global '_' in the Jinja2 environment, enabling template-level i18n.

    Args:
        env (Environment): The Jinja2 environment to configure.
        template_path (str): The relative path to the template being rendered.
        request (Request): The incoming request object, used to extract the user's locale.

    Side Effects:
        Modifies env.globals by setting the '_' key to the appropriate translation function.

    Fallback:
        If no translation is found, sets '_' to an identity function (returns input string).
    """
    locale = request.cookies.get("locale", "en")

    for base_path in settings.TEMPLATE_DIRS:
        full_path = base_path / template_path
        if full_path.exists():
            parts = full_path.parts
            if "modules" in parts:
                # It's a module template → resolve module name
                try:
                    mod_index = parts.index("modules")
                    module_name = parts[mod_index + 1]
                    i18n_root = settings.MODULES_DIR / module_name / "i18n"
                    env.globals["_"] = get_translations(i18n_root, locale)
                    return
                except Exception:
                    pass
            elif "core" in parts:
                # It's a core template → use core-level locale if needed
                i18n_root = settings.CORE_DIR / "i18n"
                env.globals["_"] = get_translations(i18n_root, locale)
                return

    # Fallback: no translation found
    env.globals["_"] = lambda s: s

# ─────────────────────────────────────────────────────────────────────────────
# Base Template Resolver
# ─────────────────────────────────────────────────────────────────────────────

def guess_base_template(template_path: str) -> str | None:
    """
    Attempts to determine the appropriate base template filename for a given template path.

    This function iterates through the directories specified in `settings.TEMPLATE_DIRS`, 
    constructs the full path to the template, and checks if it exists. If the template is found 
    within a directory named "modules" or "core", it returns the base template name in the format 
    `<module_or_core_name>_base.html`, where `<module_or_core_name>` is the immediate subdirectory 
    following "modules" or "core" in the path.

    Args:
        template_path (str): The relative path to the template file.

    Returns:
        str | None: The guessed base template filename if found, otherwise None.
    """
    for base_path in settings.TEMPLATE_DIRS:
        full_path = base_path / template_path
        if full_path.exists():
            parts = full_path.parts
            try:
                if "modules" in parts:
                    mod_index = parts.index("modules")
                    return f"{parts[mod_index + 1]}_base.html"
                elif "core" in parts:
                    mod_index = parts.index("core")
                    return f"{parts[mod_index + 1]}_base.html"
            except IndexError:
                return None
    return None

# ─────────────────────────────────────────────────────────────────────────────
# Render Entrypoints
# ─────────────────────────────────────────────────────────────────────────────

def render(template_path: str, request: Request, context: dict) -> HTMLResponse:
    """
    Renders a template with the given context and request, handling HTMX requests and base template injection.

    Args:
        template_path (str): The path to the template to render.
        request (Request): The current HTTP request object.
        context (dict): The context dictionary to pass to the template.

    Returns:
        HTMLResponse: The rendered HTML response.

    Raises:
        ValueError: If attempting to render a base layout template directly.

    Behavior:
        - Injects the request into the context.
        - Applies locale settings to the template environment.
        - If the request is an HTMX request, renders the template directly.
        - Prevents direct rendering of base layout templates.
        - If a base template is detected, injects the content template and renders the base.
        - Otherwise, renders the specified template.
    """
    context["request"] = request

    apply_module_locale(env, template_path, request)

    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(template_path, context)

    if template_path.endswith("_base.html"):
        raise ValueError(f"Refusing to inject layout template directly: {template_path}")

    base_template = guess_base_template(template_path)
    if base_template:
        context["content_template"] = template_path
        return templates.TemplateResponse(base_template, context)

    return templates.TemplateResponse(template_path, context)


def render_to_string(template_name: str, request: Request, context: dict) -> str:
    """
    Renders a template to a string using the provided template name, request, and context.

    Args:
        template_name (str): The name of the template to render.
        request (Request): The current HTTP request object.
        context (dict): The context data to pass to the template.

    Returns:
        str: The rendered template as a string.
    """
    context["request"] = request
    apply_module_locale(env, template_name, request)
    return templates.get_template(template_name).render(context)
