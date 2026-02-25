DEFAULT_FG = "#000000"
DEFAULT_BG = "#ffffff"
DEFAULT_SIZE = 10
DEFAULT_BORDER = 4
DEFAULT_GRADIENT = "horizontal"

NAMED_COLORS = {
    "black": "#000000",
    "white": "#ffffff",
    "red": "#ff0000",
    "green": "#008000",
    "blue": "#0000ff",
    "yellow": "#ffff00",
    "orange": "#ffa500",
    "purple": "#800080",
    "pink": "#ffc0cb",
    "cyan": "#00ffff",
    "magenta": "#ff00ff",
    "lime": "#00ff00",
    "indigo": "#4b0082",
    "violet": "#ee82ee",
    "teal": "#008080",
    "brown": "#a52a2a",
    "gold": "#ffd700",
    "silver": "#c0c0c0",
    "gray": "#808080",
    "grey": "#808080",
    "navy": "#000080",
    "coral": "#ff7f50",
    "salmon": "#fa8072",
    "turquoise": "#40e0d0",
    "beige": "#f5f5dc",
    "mint": "#98ff98",
    "lavender": "#e6e6fa",
    "maroon": "#800000",
    "olive": "#808000",
    "crimson": "#dc143c",
}

GRADIENT_TYPES = [
    "horizontal",
    "vertical",
    "diagonal",
    "diagonal_reverse",
    "center",
    "center_reverse",
]


def resolve_color(value: str, fallback: str = DEFAULT_FG) -> str:
    if not value:
        return fallback

    value = value.strip().lower()

    if value in NAMED_COLORS:
        return NAMED_COLORS[value]

    # Handle hex with or without #
    hex_val = value if value.startswith("#") else f"#{value}"
    valid_lengths = [4, 7]  # #rgb or #rrggbb
    if hex_val.startswith("#") and len(hex_val) in valid_lengths:
        try:
            int(hex_val[1:], 16)
            return hex_val
        except ValueError:
            pass

    # Unrecognised — default to black
    return fallback