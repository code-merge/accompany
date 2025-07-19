class SessionManager:
    """
    SessionManager provides a convenient interface for managing session data, 
    particularly for handling form data and errors within a web application context.

    Args:
        request: The HTTP request object containing the session.

    Methods:
        get_form(key: str) -> dict:
            Retrieve the form data dictionary stored in the session under the given key.

        get_errors(key: str) -> dict:
            Retrieve the errors dictionary stored in the session under the given key.

        save_form(key: str, form: dict, errors: dict):
            Save form data and associated errors to the session under the specified key.

        clear_errors(key: str):
            Remove the errors dictionary for the specified key from the session.

        clear_form(key: str):
            Remove the form data dictionary for the specified key from the session.

        get(key: str, default=None):
            Retrieve a value from the session by key, returning default if not found.

        set(key: str, value):
            Set a value in the session under the specified key.

        pop(key: str, default=None):
            Remove and return a value from the session by key, returning default if not found.

        exists(key: str) -> bool:
            Check if a key exists in the session.

        clear_onboarding_state():
            Remove all onboarding-related keys and their associated data from the session.
    """
    def __init__(self, request):
        self.session = request.session

    # ── Forms & Errors ─────────────────────────────────────────────────────────
    def get_form(self, key: str) -> dict:
        return self.session.get(f"{key}_form", {})

    def get_errors(self, key: str) -> dict:
        return self.session.get(f"{key}_errors", {})

    def save_form(self, key: str, form: dict, errors: dict):
        self.session[f"{key}_form"]   = form
        self.session[f"{key}_errors"] = errors

    def clear_errors(self, key: str):
        self.session.pop(f"{key}_errors", None)

    def clear_form(self, key: str):
        self.session.pop(f"{key}_form", None)

    # ── Generic Key Access ─────────────────────────────────────────────────────
    def get(self, key: str, default=None):
        return self.session.get(key, default)

    def set(self, key: str, value):
        self.session[key] = value

    def pop(self, key: str, default=None):
        return self.session.pop(key, default)

    def exists(self, key: str) -> bool:
        return key in self.session

    # ── Bulk Cleanup ───────────────────────────────────────────────────────────
    def clear_onboarding_state(self):
        keys = [
            "db_type",
            "__admin_pw",
            "dbsetup_standard_form", "dbsetup_standard_errors",
            "dbsetup_custom_form", "dbsetup_custom_errors",
            "admin_form", "admin_errors",
            "company_form", "company_errors",
            "system_form", "system_errors"
        ]
        for key in keys:
            self.session.pop(key, None)
