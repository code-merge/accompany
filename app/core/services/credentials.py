import os
import uuid
from pathlib import Path
from configparser import RawConfigParser
from typing import Union

# Constants
INI_SUFFIX = ".ini"
PEM_SUFFIX = ".pem"
TRUE_VALUES = {"1", "true", "yes"}

# Base directory for INI + cert storage (mode 700)
def ensure_cred_paths() -> tuple[Path, Path]:
    """
    Ensures the existence of credential directories in the user's home directory.

    Creates the base directory '~/.accompany' and its 'certs' subdirectory with permissions set to 700 if they do not already exist.

    Returns:
        tuple[Path, Path]: A tuple containing the paths to the base directory and the 'certs' subdirectory.
    """
    base = Path.home() / ".accompany"
    certs = base / "certs"
    base.mkdir(exist_ok=True, mode=0o700)
    certs.mkdir(exist_ok=True, mode=0o700)
    return base, certs

_CRED_DIR, _CERT_DIR = ensure_cred_paths()


def write_db_creds(
    profile: str,
    creds: dict[str, Union[str, int, bool]],
    ssl_cert_bytes: bytes | None = None) -> None:
    
    """
    Writes database credentials and optional SSL certificate to configuration files.

    Args:
        profile (str): The profile name to associate with the credentials. Must not be empty or whitespace.
        creds (dict[str, Union[str, int, bool]]): A dictionary containing database credential key-value pairs.
        ssl_cert_bytes (bytes | None, optional): Optional SSL certificate bytes to be saved as a PEM file. Defaults to None.

    Raises:
        AssertionError: If the profile name is empty or only whitespace.

    Side Effects:
        - Writes the credentials to an INI file in the credentials directory.
        - If ssl_cert_bytes is provided, writes the certificate to a PEM file and stores its path in the INI file.
        - Sets file permissions to be readable and writable only by the owner (mode 0o600).
        - Ignores exceptions raised during chmod operations.
    """
    
    """
    Write ~/.accompany/<profile>.ini securely.
    If ssl_cert_bytes is provided, save a .pem in certs/ and record its path in the ini.
    """
    
    assert profile.strip(), "Profile name must not be empty"

    ini_path = _CRED_DIR / f"{profile}{INI_SUFFIX}"
    parser = RawConfigParser()
    parser["database"] = {str(k): str(v) for k, v in creds.items()}

    if ssl_cert_bytes:
        pem_name = f"{profile}-{uuid.uuid4().hex}{PEM_SUFFIX}"
        pem_path = _CERT_DIR / pem_name
        try:
            with open(pem_path, "wb") as f:
                f.write(ssl_cert_bytes)
            os.chmod(pem_path, 0o600)
            parser["database"]["ssl_cert"] = str(pem_path)
        except Exception:
            pass  # Ignore chmod errors gracefully

    with open(ini_path, "w") as f:
        parser.write(f)
    try:
        os.chmod(ini_path, 0o600)
    except Exception:
        pass


def read_db_creds(profile: str) -> dict[str, Union[str, int, bool]]:
    
    """
    Reads database credentials from an INI file located at ~/.accompany/<profile>.ini.
    Args:
        profile (str): The profile name used to locate the credentials file.
    Returns:
        dict[str, Union[str, int, bool]]: A dictionary containing the database credentials,
        with values automatically cast to the appropriate types (int for 'port', bool for 'ssl', and str for others).
    Raises:
        KeyError: If the 'database' section is missing in the INI file.
        FileNotFoundError: If the credentials file does not exist.
        ValueError: If type casting fails for any of the expected fields.
    

    Read ~/.accompany/<profile>.ini and return a typed dict.
    """
    ini_path = _CRED_DIR / f"{profile}{INI_SUFFIX}"
    parser = RawConfigParser()
    parser.read(ini_path)

    raw = dict(parser["database"])

    def cast(k: str, v: str) -> Union[str, int, bool]:
        if k == "port":
            return int(v)
        if k == "ssl":
            return v.lower() in TRUE_VALUES
        return v

    return {k: cast(k, v) for k, v in raw.items()}


def get_available_profiles() -> list[str]:
    """
    List all stored profiles in ~/.accompany.
    """
    return [p.stem for p in _CRED_DIR.glob(f"*{INI_SUFFIX}")]
