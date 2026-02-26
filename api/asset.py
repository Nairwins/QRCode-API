from pathlib import Path
from PIL import ImageColor

ICON_DIR  = Path(__file__).parent / "icon"
INNER_DIR = Path(__file__).parent / "inner"
OUTER_DIR = Path(__file__).parent / "outer"

ICONS = {
    "gold":  ICON_DIR  / "gold.png",
    "laser": ICON_DIR  / "laser.png",
}

INNER_EYES = {
    "flower": INNER_DIR / "flower.png",
}

OUTER_EYES = {
    "eye": OUTER_DIR / "eye.png",
}

def parse_color(value: str, fallback: str = "black") -> tuple:
    if not value:
        return ImageColor.getrgb(fallback)
    try:
        return ImageColor.getrgb(value if value.startswith("#") else f"#{value}")
    except (ValueError, AttributeError):
        try:
            return ImageColor.getrgb(value)
        except (ValueError, AttributeError):
            return ImageColor.getrgb(fallback)