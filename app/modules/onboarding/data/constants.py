from pathlib import Path
from app.core.utils.svg_utils import load_svg

ICON_DIR = Path("app/modules/onboarding/static/images")

steps = [
    {"icon": load_svg(ICON_DIR / "handshake.svg"), "title": "onboarding_welcome", "description": "onboarding_welcome_desc"},
]