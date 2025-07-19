from pydantic import BaseModel, field_validator
from app.modules.onboarding.data.constants import LANGUAGES, THEMES
from .validators import not_blank

class SystemData(BaseModel):
    """
    SystemData model represents system configuration information for onboarding.

    Attributes:
        country_code (str): The ISO country code (e.g., 'US', 'IN').
        timezone (str): The timezone identifier (e.g., 'UTC', 'Asia/Kolkata').
        currency (str): The currency code (e.g., 'USD', 'INR').
        language (str): The language code, must be one of the supported LANGUAGES.
        theme (str): The UI theme, must be one of the supported THEMES.
        modules (list[str]): List of enabled module names.

    Validators:
        - Ensures 'country_code', 'timezone', and 'currency' are not blank.
        - Validates 'language' against the allowed LANGUAGES.
        - Validates 'theme' against the allowed THEMES.
    """
    country_code: str
    timezone: str
    currency: str
    language: str
    theme: str
    modules: list[str]

    @field_validator("country_code", "timezone", "currency", mode="before")
    def validate_required(cls, v): return not_blank(v)

    @field_validator("language")
    def validate_language(cls, v):
        if v not in LANGUAGES:
            raise ValueError("Select a valid language.")
        return v

    @field_validator("theme")
    def validate_theme(cls, v):
        if v not in THEMES:
            raise ValueError("Select a valid theme.")
        return v
