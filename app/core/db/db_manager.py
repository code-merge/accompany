import ssl
import string
import secrets
import asyncpg
from pathlib import Path
from passlib.hash import bcrypt
from urllib.parse import quote_plus
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from app.core.config.config import settings
from app.core.services.credentials import write_db_creds
from app.modules.onboarding.data.constants import LANGUAGES

def generate_password(length: int = 20) -> str:
    """
    Generates a random password string of a specified length.

    The password consists of uppercase and lowercase ASCII letters, digits, and a selection of special characters.

    Args:
        length (int, optional): The length of the generated password. Defaults to 20.

    Returns:
        str: A randomly generated password string.
    """
    charset = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(secrets.choice(charset) for _ in range(length))

def create_standard_db(db_name: str) -> tuple[bool, dict, str]:
    """
    Creates a new PostgreSQL database with a dedicated admin user and grants necessary privileges.

    Args:
        db_name (str): The name of the database to create.

    Returns:
        tuple[bool, dict, str]: 
            - A boolean indicating success or failure.
            - A dictionary containing the database credentials if successful, otherwise empty.
            - A message describing the result of the operation.

    The function performs the following steps:
        1. Generates a unique admin username and password for the new database.
        2. Connects to the PostgreSQL server as a superuser.
        3. Creates the new database and admin user.
        4. Grants all privileges on the new database to the admin user.
        5. Grants usage and create privileges on the public schema to the admin user.
        6. Stores the credentials using `write_db_creds`.
        7. Returns the result of the operation, credentials, and a status message.

    Exceptions:
        Returns a failure status, empty credentials, and an error message if any step fails.
    """
    admin_user = f"{db_name}_admin"
    admin_pass = generate_password()

    super_url = (
        f"postgresql+psycopg://{settings.POSTGRES_SUPERUSER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/postgres"
    )
    engine = create_engine(super_url, isolation_level="AUTOCOMMIT")

    try:
        with engine.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))

            escaped_user = admin_user.replace('"', '""')  
            escaped_pass = admin_pass.replace("'", "''")  
            conn.execute(text(f"CREATE USER \"{escaped_user}\" WITH ENCRYPTED PASSWORD '{escaped_pass}'"))

            # conn.execute(text(f"CREATE USER {admin_user} WITH ENCRYPTED PASSWORD '{admin_pass}'"))
            conn.execute(text(f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO {admin_user}'))

        target_url = (
            f"postgresql+psycopg://{settings.POSTGRES_SUPERUSER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{db_name}"
        )
        target_engine = create_engine(target_url, isolation_level="AUTOCOMMIT")
        with target_engine.connect() as conn:
            conn.execute(text(f'GRANT USAGE ON SCHEMA public TO {admin_user}'))
            conn.execute(text(f'GRANT CREATE ON SCHEMA public TO {admin_user}'))

        creds = {
            "db_name": db_name,
            "user": admin_user,
            "password": admin_pass,
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
            "ssl": False
        }
        write_db_creds(db_name, creds)
        return True, creds, f"✅ Created DB '{db_name}' with scoped admin '{admin_user}'"
    except Exception as e:
        return False, {}, f"❌ DB setup failed: {e}"
    

async def create_custom_db(form: dict) -> tuple[bool, dict, str]:
    """
    Asynchronously creates and validates a custom database connection using provided form data.

    Attempts to connect to a PostgreSQL database using credentials and optional SSL certificate information from the input dictionary. If the connection is successful, credentials (and optionally the SSL certificate bytes) are persisted using `write_db_creds`. Returns a tuple indicating success, the credentials dictionary, and a status message.

    Args:
        form (dict): A dictionary containing database connection parameters:
            - "user" (str): Database username.
            - "password" (str): Database password.
            - "db_name" (str): Database name.
            - "host" (str): Database host.
            - "port" (int or str): Database port.
            - "ssl" (bool, optional): Whether to use SSL.
            - "ssl_cert_path" (str, optional): Path to SSL certificate file for connection.
            - "ssl_cert" (str, optional): Path to SSL certificate file to persist.

    Returns:
        tuple[bool, dict, str]: 
            - Success status (bool).
            - Credentials dictionary (dict) if successful, else empty dict.
            - Status message (str) describing the result.
    """

    ssl_ctx = None
    if form.get("ssl"):
        cert_path = form.get("ssl_cert_path")
        print(cert_path)
        if not cert_path or not Path(cert_path).exists():
            return False, {}, "❌ SSL enabled but certificate not found on disk."
        ssl_ctx = ssl.create_default_context(cafile=cert_path)

    try:
        conn = await asyncpg.connect(
            user=form["user"],
            password=form["password"],
            database=form["db_name"],
            host=form["host"],
            port=form["port"],
            ssl=ssl_ctx,
        )
        await conn.close()

        # Prepare creds dict for INI
        creds = {
            "db_name":  form["db_name"],
            "user":     form["user"],
            "password": form["password"],
            "host":     form["host"],
            "port":     form["port"],
            "ssl":      form.get("ssl", False),
        }

        # Read and persist the actual PEM bytes if provided
        pem_bytes = None
        cert_path = form.get("ssl_cert")
        if cert_path and Path(cert_path).exists():
            pem_bytes = Path(cert_path).read_bytes()

        # Write to ~/.accompany
        write_db_creds(
            profile=form["db_name"],
            creds=creds,
            ssl_cert_bytes=pem_bytes
        )

        return True, creds, f"✅ Connected to custom DB '{form['db_name']}' and saved credentials."
    except Exception as e:
        return False, {}, f"❌ Could not connect to remote DB: {e}"
    

def get_db_admin_engine(creds: dict) -> AsyncEngine:
    """
    Creates and returns an asynchronous SQLAlchemy engine for connecting to a PostgreSQL database using asyncpg.

    Args:
        creds (dict): A dictionary containing database credentials with the following keys:
            - "user": Username for database authentication.
            - "password": Password for database authentication.
            - "host": Hostname or IP address of the database server.
            - "port": Port number on which the database server is listening.
            - "db_name": Name of the database to connect to.

    Returns:
        AsyncEngine: An asynchronous SQLAlchemy engine instance configured with the provided credentials.
    """
    user = quote_plus(creds["user"])
    pw   = quote_plus(creds["password"])
    host = creds["host"]
    port = creds["port"]
    db   = creds["db_name"]

    url = f"postgresql+asyncpg://{user}:{pw}@{host}:{port}/{db}"
    return create_async_engine(url, future=True, echo=False)

async def create_system_admin_user(engine: AsyncEngine, email: str, password: str) -> tuple[bool, str]:
    """
    Asynchronously creates a system admin user in the database.

    This function ensures the 'users' table exists, hashes the provided password,
    and inserts a new user with the 'system_admin' role. If the email already exists,
    it returns an appropriate error message.

    Args:
        engine (AsyncEngine): The SQLAlchemy asynchronous engine for database connection.
        email (str): The email address (used as username) for the new admin user.
        password (str): The plaintext password for the new admin user.

    Returns:
        tuple[bool, str]: A tuple where the first element indicates success (True) or failure (False),
                          and the second element is a message describing the result.
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE,
                    hashed_password TEXT,
                    role TEXT DEFAULT 'user'
                );
            """))
            hashed_pw = bcrypt.using(rounds=12).hash(password)
            await conn.execute(text("""
                INSERT INTO users (username, hashed_password, role)
                VALUES (:email, :pw, 'system_admin');
            """), {"email": email, "pw": hashed_pw})
        return True, "✅ System admin user created"
    except IntegrityError:
        return False, f"❌ Email '{email}' already exists"
    except Exception as e:
        return False, f"❌ Failed to create admin: {e}"

async def create_company_record(engine: AsyncEngine, name: str, industry: str) -> tuple[bool, str]:
    """
    Asynchronously creates a company record in the database.

    If the 'company' table does not exist, it will be created. Then, a new record with the provided
    company name and industry is inserted.

    Args:
        engine (AsyncEngine): The SQLAlchemy asynchronous engine to use for database operations.
        name (str): The name of the company to be added.
        industry (str): The industry of the company.

    Returns:
        tuple[bool, str]: A tuple where the first element indicates success (True) or failure (False),
                          and the second element is a message describing the result.
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS company (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    industry TEXT NOT NULL
                );
            """))
            await conn.execute(text("""
                INSERT INTO company (name, industry)
                VALUES (:name, :industry);
            """), {"name": name, "industry": industry})
        return True, "✅ Company record created"
    except Exception as e:
        return False, f"❌ Failed to create company: {e}"

async def seed_languages(engine: AsyncEngine) -> str:
    """
    Seeds the 'languages' table in the database with language codes and their labels.

    This function creates the 'languages' table if it does not exist, and inserts language codes
    from the global LANGUAGES list, using the code as the label in uppercase. Duplicate codes are ignored.

    Args:
        engine (AsyncEngine): The SQLAlchemy asynchronous engine to use for database operations.

    Returns:
        str: A message indicating whether the seeding was successful or failed.
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS languages (
                    id SERIAL PRIMARY KEY,
                    code TEXT UNIQUE,
                    label TEXT
                );
            """))
            for code in LANGUAGES:
                label = code.upper()
                await conn.execute(text("""
                    INSERT INTO languages (code, label)
                    VALUES (:code, :label)
                    ON CONFLICT (code) DO NOTHING;
                """), {"code": code, "label": label})
        return "✔️ Languages seeded"
    except Exception as e:
        return f"❌ Failed to seed languages: {e}"

async def seed_modules(engine: AsyncEngine, modules: list[str]) -> str:
    """
    Seeds the 'modules' table in the database with the provided list of module names.

    If the 'modules' table does not exist, it will be created with columns for id, name, and enabled status.
    Each module name in the provided list will be inserted into the table with 'enabled' set to TRUE.
    If a module name already exists, it will not be inserted again.

    Args:
        engine (AsyncEngine): The asynchronous SQLAlchemy engine to use for database operations.
        modules (list[str]): A list of module names to seed into the database.

    Returns:
        str: A message indicating whether the seeding was successful or failed, including error details if any.
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS modules (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE,
                    enabled BOOLEAN DEFAULT TRUE
                );
            """))
            for mod in modules:
                await conn.execute(text("""
                    INSERT INTO modules (name, enabled)
                    VALUES (:name, TRUE)
                    ON CONFLICT (name) DO NOTHING;
                """), {"name": mod})
        return "✔️ Modules seeded"
    except Exception as e:
        return f"❌ Failed to seed modules: {e}"
