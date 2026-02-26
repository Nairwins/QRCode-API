from pathlib import Path
from PIL import ImageColor

ICON_DIR = Path(__file__).parent / "icon"

ICONS = {
    "gold": ICON_DIR / "gold.png",
    "laser": ICON_DIR / "laser.png",
}

def parse_color(value: str, fallback: str = "black") -> tuple:
    """Accept #hex, hex without #, or named colors like 'red'. Falls back to black."""
    if not value:
        return ImageColor.getrgb(fallback)
    try:
        return ImageColor.getrgb(value if value.startswith("#") else f"#{value}")
    except (ValueError, AttributeError):
        try:
            return ImageColor.getrgb(value)
        except (ValueError, AttributeError):
            return ImageColor.getrgb(fallback)