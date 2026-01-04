# app/modules/onboarding/models/admin_user_model.py

from pydantic import BaseModel, field_validator
from .validators import not_blank, valid_email

class AdminData(BaseModel):
    """
    AdminData model for representing administrative user information.

    Attributes:
        full_name (str): The full name of the admin user. Must not be blank.
        email (str): The email address of the admin user. Must be a valid email.

    Validators:
        validate_name: Ensures that 'full_name' is not blank.
        validate_email: Ensures that 'email' is a valid email address.
    """
    full_name: str
    email: str

    @field_validator("full_name")
    def validate_name(cls, v): return not_blank(v)

    @field_validator("email")
    def validate_email(cls, v): return valid_email(v)
