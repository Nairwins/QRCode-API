from pathlib import Path
from PIL import ImageColor

ICON_DIR  = Path(__file__).parent / "icon"
INNER_DIR = Path(__file__).parent / "inner"
OUTER_DIR = Path(__file__).parent / "outer"

ICONS = {
    "facebook":  ICON_DIR / "facebook.png",
    "gmail":     ICON_DIR / "gmail.png",
    "gold":      ICON_DIR / "gold.png",
    "instagram": ICON_DIR / "instagram.png",
    "linkedin":  ICON_DIR / "linkedin.png",
    "paypal":    ICON_DIR / "paypal.png",
    "phone":     ICON_DIR / "phone.png",
    "pinterest": ICON_DIR / "pinterest.png",
    "snapchat":  ICON_DIR / "snapchat.png",
    "spotify":   ICON_DIR / "spotify.png",
    "telegram":  ICON_DIR / "telegram.png",
    "twitch":    ICON_DIR / "twitch.png",
    "twitter":   ICON_DIR / "twitter.png",
    "whatsapp":  ICON_DIR / "whatsapp.png",
    "wifi":      ICON_DIR / "wifi.png",
    "youtube":   ICON_DIR / "youtube.png",
}

INNER_EYES = {
    "clog":    INNER_DIR / "clog.png",
    "cloud":   INNER_DIR / "cloud.png",
    "diamond": INNER_DIR / "diamond.png",
    "flower":  INNER_DIR / "flower.png",
    "heart":   INNER_DIR / "heart.png",
    "petal":   INNER_DIR / "petal.png",
    "rounded": INNER_DIR / "rounded.png",
    "sphere":  INNER_DIR / "sphere.png",
    "star":    INNER_DIR / "star.png",
    "target":  INNER_DIR / "target.png",
    "x":       INNER_DIR / "x.png",
}

OUTER_EYES = {
    "bloop":   OUTER_DIR / "bloop.png",
    "circle":  OUTER_DIR / "circle.png",
    "corner":  OUTER_DIR / "corner.png",
    "eye":     OUTER_DIR / "eye.png",
    "floop":   OUTER_DIR / "floop.png",
    "octagon": OUTER_DIR / "octagon.png",
    "rounded": OUTER_DIR / "rounded.png",
    "rounder": OUTER_DIR / "rounder.png",
    "target":  OUTER_DIR / "target.png",
    "zig":     OUTER_DIR / "zig.png",
}

# Available dot styles
DOT_STYLES = {"square", "dot", "block", "rounded", "diamond", "smooth", "vertical", "horizontal", "aura"}


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