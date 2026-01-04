from pathlib import Path

def load_svg(path: Path, size: str = "w-4 h-4") -> str:
    """
    Load an inline SVG and inject Tailwind size classes.
    Returns an empty string if file is missing.
    """
    try:
        svg = path.read_text(encoding="utf-8")
        return svg.replace("<svg", f'<svg class="{size}"')
    except FileNotFoundError:
        return ""
