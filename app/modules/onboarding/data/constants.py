from pathlib import Path
from app.core.utils.svg_utils import load_svg

ICON_DIR = Path("app/modules/onboarding/static/images")

steps = [
    {"icon": load_svg(ICON_DIR / "handshake.svg"), "title": "onboarding_welcome", "description": "onboarding_welcome_desc"},
    {"icon": load_svg(ICON_DIR / "copyright.svg"), "title": "onboarding_licence", "description": "onboarding_licence_desc"},
    {"icon": load_svg(ICON_DIR / "database.svg"), "title": "onboarding_database_setup", "description": "onboarding_database_setup_desc"},
    {"icon": load_svg(ICON_DIR / "admin_user.svg"), "title": "onboarding_admin_user_setup", "description": "onboarding_admin_user_setup_desc"},
]