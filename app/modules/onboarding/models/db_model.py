# app/modules/onboarding/models/db_model.py

from pydantic import BaseModel, field_validator
from .validators import not_blank, matches_pattern

class StandardDBData(BaseModel):
    """
    StandardDBData represents a database model with a single field for the database name.

    Attributes:
        db_name (str): The name of the database. Must contain only letters, numbers, and underscores.

    Validators:
        validate_db_name: Ensures that db_name matches the pattern allowing only letters, numbers, and underscores.
    """
    db_name: str

    @field_validator("db_name")
    def validate_db_name(cls, v):
        return matches_pattern(v, r"^[A-Za-z0-9_]+$", "Only letters, numbers, and underscore allowed.")

class CustomDBData(BaseModel):
    """
    CustomDBData represents the configuration required to connect to a custom database.

    Attributes:
        db_name (str): The name of the database.
        host (str): The hostname or IP address of the database server.
        port (int): The port number on which the database server is listening.
        user (str): The username used to authenticate with the database.
        password (str): The password used to authenticate with the database.
        ssl (bool): Indicates whether SSL should be used for the connection.

    Validators:
        Ensures that 'db_name', 'host', 'user', and 'password' fields are not blank.
    """
    db_name: str
    host: str
    port: int
    user: str
    password: str
    ssl: bool

    @field_validator("db_name", "host", "user", "password", mode="before")
    def validate_fields(cls, v): return not_blank(v)
