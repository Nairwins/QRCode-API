from pathlib import Path
from PIL import ImageColor

ICON_DIR  = Path(__file__).parent / "icon"
INNER_DIR = Path(__file__).parent / "inner"
OUTER_DIR = Path(__file__).parent / "outer"

ICONS = {
    "gold":  ICON_DIR / "gold.png",
    "laser": ICON_DIR / "laser.png",
}

INNER_EYES = {
    "cloud":   INNER_DIR / "cloud.png",
    "flower":  INNER_DIR / "flower.png",
    "heart":   INNER_DIR / "heart.png",
    "rounded": INNER_DIR / "rounded.png",
    "sphere":  INNER_DIR / "sphere.png",
    "target":  INNER_DIR / "target.png",
    "x":       INNER_DIR / "x.png",
}

OUTER_EYES = {
    "circle":  OUTER_DIR / "circle.png",
    "eye":     OUTER_DIR / "eye.png",
    "octagon": OUTER_DIR / "octagon.png",
    "rounded": OUTER_DIR / "rounded.png",
    "rounder": OUTER_DIR / "rounder.png",
    "target":  OUTER_DIR / "target.png",
    "zig":     OUTER_DIR / "zig.png",
}

# Available dot styles
DOT_STYLES = {"square", "dot", "block", "rounded", "diamond", "smooth", "vertical", "horizontal", "aura"}

# Built-in eye styles (no PNG needed)
OUTER_BUILTIN_STYLES = {"square", "rounded", "circle", "dots"}
INNER_BUILTIN_STYLES = {"square", "rounded", "circle", "diamond"}

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