import pytest
from pydantic import ValidationError
from app.modules.onboarding.models.admin_user_model import AdminData
from app.modules.onboarding.models.company_model import CompanyData
from app.modules.onboarding.models.db_model import StandardDBData, CustomDBData
from app.modules.onboarding.models.system_info_model import SystemData

def test_admin_data_valid():
    """
    Validates that `AdminData` accepts correct input.

    Asserts:
    --------
    - The email field is retained correctly when a valid email is provided.
    - No `ValidationError` is raised.
    """
    d = AdminData(full_name="John", email="john@mail.com")
    assert d.email == "john@mail.com"

def test_admin_data_invalid_email():
    """
    Ensures `AdminData` raises a `ValidationError` for an invalid email format.

    Asserts:
    --------
    - Validation fails when email is not properly formatted.
    - The error is correctly captured using `pytest.raises`.
    """
    with pytest.raises(ValidationError):
        AdminData(full_name="John", email="invalid")

def test_company_data_blank():
    """
    Ensures that `CompanyData` requires a non-empty company name and industry.

    Asserts:
    --------
    - `ValidationError` is raised when both fields are empty.
    """
    with pytest.raises(ValidationError):
        CompanyData(company_name="", industry="")

def test_standard_db_valid():
    """
    Verifies that `StandardDBData` correctly stores a valid database name.

    Asserts:
    --------
    - The db_name field matches the input value.
    - No exceptions are raised during initialization.
    """
    assert StandardDBData(db_name="accompany_db").db_name == "accompany_db"

def test_custom_db_missing_user():
    """
    Confirms that `CustomDBData` fails validation when the user field is empty.

    Asserts:
    --------
    - A `ValidationError` is raised due to missing required credentials.
    - Validates enforcement of non-empty `user` field.
    """
    with pytest.raises(ValidationError):
        CustomDBData(db_name="test", host="localhost", port=5432, user="", password="pass", ssl=False)

def test_system_data_invalid_language():
    """
    Validates that `SystemData` rejects unsupported language codes.

    Asserts:
    --------
    - A `ValidationError` is raised when an invalid language is provided.
    - Checks model integrity against the accepted language list.
    """
    with pytest.raises(ValidationError):
        SystemData(
            country_code="IN",
            timezone="Asia/Kolkata",
            currency="INR",
            language="Klingon",
            theme="default",
            modules=[]
        )
