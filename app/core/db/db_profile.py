from app.core.services.credentials import get_available_profiles

def get_active_profile() -> str:
    # Pick most recent profile or default
    profiles = get_available_profiles()
    if not profiles:
        raise RuntimeError("No database profiles found in ~/.accompany")
    return profiles[-1]  # or use a more sophisticated selector
