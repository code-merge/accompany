# app/modules/onboarding/models/company_model.py

from pydantic import BaseModel, field_validator
from .validators import not_blank

class CompanyData(BaseModel):
    """
    CompanyData model represents basic information about a company.

    Attributes:
        company_name (str): The name of the company. Must not be blank.
        industry (str): The industry the company operates in. Must not be blank.

    Validators:
        - Ensures that both 'company_name' and 'industry' fields are not blank before assignment.
    """
    company_name: str
    industry: str

    @field_validator("company_name", "industry", mode="before")
    def validate_fields(cls, v): return not_blank(v)
