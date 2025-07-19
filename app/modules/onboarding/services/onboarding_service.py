from typing import AsyncGenerator

from app.core.db.db_manager import (
    create_standard_db,
    create_custom_db,
    get_db_admin_engine,
    create_system_admin_user,
    create_company_record,
    seed_languages,
    seed_modules
)

async def provision_site(session: dict) -> AsyncGenerator[str, None]:
    """
    Asynchronously provisions a complete ERP site based on the current onboarding session data.

    This coroutine yields progress messages in discrete steps to support Server-Sent Events (SSE)
    or streaming responses.

    Parameters:
    -----------
    session : dict
        A dictionary containing onboarding state captured across multiple steps.
        Expected keys include:
        - "db_type" : str = "standard" or "custom"
        - "db_form" : dict with DB connection or creation details
        - "admin_form" : dict containing admin email
        - "admin_password" : str
        - "company_form" : dict with company name and industry
        - "system_form" : dict with modules and preferences

    Workflow:
    ---------
    1. Initializes provisioning with a status message.
    2. Creates or connects to the target database.
    3. Constructs a SQLAlchemy engine scoped to the provisioned DB.
    4. Creates a system admin user if credentials are valid.
    5. Creates a company record.
    6. Seeds language entries into the DB.
    7. Enables selected modules.
    8. Yields a final "done" signal when provisioning completes or fails.

    Yields:
    -------
    str
        A human-readable progress message at each step. Includes emoji markers and abort notices.
        The final `"done"` message marks stream termination.

    Returns:
    --------
    AsyncGenerator[str, None]
        A stream of status messages suitable for use with FastAPI's `StreamingResponse`.

    Notes:
    ------
    - If any provisioning step fails, the coroutine will yield an appropriate error message followed by "done".
    - Messages are designed for frontend display — they include emoji prefixes like "🔧", "📦", "❌".
    - The actual DB operations are handled by async functions in `app.core.db.db_manager`.

    Example Usage:
    --------------
    async for message in provision_site(session_data):
        print("Stream:", message)
    """
    
    db_type      = session.get("db_type", "standard")
    db_form      = session.get("db_form", {})
    admin_form   = session.get("admin_form", {})
    company_form = session.get("company_form", {})
    system_form  = session.get("system_form", {})
    password     = session.get("admin_password", "").strip()

    db_name  = db_form.get("db_name", "").strip()
    email    = admin_form.get("email", "").strip()
    company  = company_form.get("company_name", "").strip()
    industry = company_form.get("industry", "").strip()
    modules  = system_form.get("modules", [])

    yield "🔧 Starting site provisioning..."

    # ── Step 1: Create or Connect to DB ─────────────────────────────
    yield "📦 Setting up database..."
    if db_type == "standard":
        ok, creds, msg = create_standard_db(db_name)
        print(msg)

    else:
        ok, creds, msg = await create_custom_db(db_form)
        print(msg)

    yield msg
    if not ok:
        print(msg)
        yield "❌ Aborting: DB provisioning failed"
        yield "done"
        return

    # ── Step 2: Build scoped engine ────────────────────────────────
    engine = get_db_admin_engine(creds)

    # ── Step 3: Create Admin ────────────────────────────────────────
    yield "👤 Creating system admin..."
    if not email or not password:
        yield "❌ Aborting: Admin credentials missing"
        yield "done"
        return

    ok, msg = await create_system_admin_user(engine, email, password)
    print(msg)
    yield msg
    if not ok:
        yield "❌ Aborting: Admin setup failed"
        yield "done"
        return

    # ── Step 4: Create Company ──────────────────────────────────────
    yield "🏢 Creating company record..."
    if not company:
        yield "❌ Aborting: Company name missing"
        yield "done"
        return

    ok, msg = await create_company_record(engine, company, industry)
    print(msg)
    yield msg
    if not ok:
        yield "❌ Aborting: Company setup failed"
        yield "done"
        return

    # ── Step 5: Seed Languages ─────────────────────────────────────
    yield "🌐 Seeding languages..."
    msg = await seed_languages(engine)
    print(msg)
    yield msg
    if msg.startswith("❌"):
        yield "❌ Aborting: Language seeding failed"
        yield "done"
        return

    # ── Step 6: Seed Modules ───────────────────────────────────────
    yield "📦 Enabling modules..."
    msg = await seed_modules(engine, modules)
    print(msg)
    yield msg
    if msg.startswith("❌"):
        yield "❌ Aborting: Module seeding failed"
        yield "done"
        return

    # ── All done ───────────────────────────────────────────────────
    yield "✅ Site provisioning complete"
    yield "done"
