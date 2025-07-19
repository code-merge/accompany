import pytest
from app.modules.onboarding.services.onboarding_service import provision_site

@pytest.mark.asyncio
async def test_provision_site_fail_on_empty_db():
    """
    Tests the provisioning workflow to ensure it correctly fails when the database name is missing.

    Scenario:
    ---------
    - Uses the "standard" database type.
    - Supplies an empty `db_name` in the session.
    - Provides valid admin, company, and system form data otherwise.

    Workflow:
    ---------
    - Calls `provision_site()` with the incomplete session.
    - Collects all messages streamed during provisioning.

    Assertions:
    -----------
    - Verifies that at least one message contains "DB provisioning failed".
    - Confirms that the provisioning stream ends with a "done" event.

    Notes:
    ------
    - This test validates that defensive checks against missing DB info are enforced.
    - Ensures graceful termination of provisioning when DB creation fails.

    Returns:
    --------
    None
    """
    session = {
        "db_type": "standard",
        "db_form": {"db_name": ""},
        "admin_form": {"email": "admin@mail.com"},
        "company_form": {"company_name": "Comp", "industry": "Tech"},
        "system_form": {"language": "en", "theme": "default", "modules": []},
        "admin_password": "secure123"
    }

    logs = []
    async for msg in provision_site(session):
        logs.append(msg)

    assert any("DB provisioning failed" in m for m in logs)
    assert "done" in logs
