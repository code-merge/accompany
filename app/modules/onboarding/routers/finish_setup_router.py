from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from app.core.session_manager import SessionManager
from app.core.templating.template_utils import render
from app.modules.onboarding.utils.context_utils import build_context
from app.modules.onboarding.services.onboarding_service import provision_site


router = APIRouter()

@router.get("/finish", response_class=HTMLResponse)
async def finish(request: Request):
    """
    Handles the GET request for the '/finish' route in the onboarding process.
    This endpoint collects data from the session manager, including database setup,
    admin, company, and system forms, to build a summary of the onboarding configuration.
    The summary includes database type and name, admin email, company name, industry,
    country, language, and selected modules. The summary is printed for debugging purposes.
    Finally, it builds the rendering context and returns the 'finish.html' template.
    Args:
        request (Request): The incoming HTTP request object.
    Returns:
        HTMLResponse: The rendered 'finish.html' page with the onboarding summary context.
    """
    sm = SessionManager(request)
    db_type      = sm.get("db_type", "standard")
    db_form      = sm.get_form("dbsetup_standard") if db_type == "standard" else sm.get_form("dbsetup_custom")
    admin_form   = sm.get_form("admin")
    company_form = sm.get_form("company")
    system_form  = sm.get("system_form", {})

    db_name = db_form.get("db_name", "") or ""

    summary = {
        "db_type":      db_type,
        "db_name":      db_name,
        "admin_email":  admin_form.get("email", ""),
        "company_name": company_form.get("company_name", ""),
        "industry":     company_form.get("industry", ""),
        "country":      system_form.get("country_code", ""),
        "language":     system_form.get("language", ""),
        "modules":      system_form.get("modules", []),
    }
    ctx = build_context(request, current_step=7, extra={"summary": summary})
    return render("finish.html", request, ctx)


@router.get("/finish-stream")
async def finish_stream(request: Request, background_tasks: BackgroundTasks):
    """
    Streams provisioning progress messages for the onboarding process via Server-Sent Events (SSE).

    Parameters:
    -----------
    request : Request
        The incoming HTTP request containing session data for provisioning.
    background_tasks : BackgroundTasks
        Background task manager for cleanup once provisioning is complete.

    Workflow:
    ---------
    - Checks if provisioning has already started or completed via session state.
    - If complete, immediately returns a `done` SSE event.
    - Otherwise:
        - Initializes a session-bound provisioning flag.
        - Constructs `session_data` from previously collected onboarding forms and session values.
        - Begins async streaming using `event_generator()`:
            - Yields log events during each provisioning step.
            - Yields a final `done` event on completion.
        - Schedules cleanup to:
            - Clear onboarding state
            - Mark onboarding as complete in session
            - Remove provisioning flag

    Returns:
    --------
    StreamingResponse
        A stream of SSE-formatted `log` and `done` events for frontend consumption.
    """
    
    sm = SessionManager(request)
    if sm.get("provisioning_started") or sm.get("onboarding_complete"):
        return StreamingResponse(
            iter(["event: done\ndata: done\n\n"]),
            media_type="text/event-stream"
        )

    sm.set("provisioning_started", True)
    done_flag = {"done": False}

    db_type = sm.get("db_type", "standard")
    session_data = {
        "db_type":      db_type,
        "db_form":      sm.get_form("dbsetup_standard") if db_type == "standard" else sm.get_form("dbsetup_custom"),
        "admin_form":   sm.get_form("admin"),
        "company_form": sm.get_form("company"),
        "system_form":  sm.get("system_form", {}),
        "admin_password": sm.pop("__admin_pw", ""),
        "ssl_cert":     sm.get("ssl_cert_path", None),
    }

    async def event_generator():
        async for msg in provision_site(session_data):
            yield f"event: log\ndata: {msg}\n\n" if msg != "done" else "event: done\ndata: done\n\n"
            if msg == "done":
                done_flag["done"] = True

    def cleanup():
        if done_flag["done"]:
            sm.clear_onboarding_state()
            sm.set("onboarding_complete", True)
            sm.pop("provisioning_started", None)

    background_tasks.add_task(cleanup)
    return StreamingResponse(event_generator(), media_type="text/event-stream")
