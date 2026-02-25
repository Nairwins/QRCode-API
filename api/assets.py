import os

DEFAULT_FG = "#000000"
DEFAULT_BG = "#ffffff"
DEFAULT_SIZE = 10
DEFAULT_BORDER = 4
DEFAULT_GRADIENT = "horizontal"
DEFAULT_SHAPE = "square"

INNER_DIR = os.path.join(os.path.dirname(__file__), "api/inner")
OUTER_DIR = os.path.join(os.path.dirname(__file__), "api/outer")

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

DOT_SHAPES = [
    "square", "circle", "dot", "rounded", "smooth",
    "diamond", "diamond_small", "star4", "star5", "cross",
    "heart", "triangle_up", "triangle_down", "hexagon", "octagon",
    "arrow_right", "vertical_line", "horizontal_line", "x_shape", "ring", "bars",
]

GRADIENT_TYPES = [
    "horizontal", "vertical", "diagonal",
    "diagonal_reverse", "center", "center_reverse",
]


def resolve_color(value: str, fallback: str = DEFAULT_FG) -> str:
    if not value:
        return fallback

    value = value.strip().lower()

    if value in NAMED_COLORS:
        return NAMED_COLORS[value]

    hex_val = value if value.startswith("#") else f"#{value}"
    if hex_val.startswith("#") and len(hex_val) in [4, 7]:
        try:
            int(hex_val[1:], 16)
            return hex_val
        except ValueError:
            pass

    return fallback


def list_svg_shapes(folder: str) -> list:
    if not os.path.isdir(folder):
        return []
    return [os.path.splitext(f)[0] for f in os.listdir(folder) if f.endswith(".svg")]


def get_svg_path(folder: str, name: str) -> str | None:
    path = os.path.join(folder, f"{name}.svg")
    return path if os.path.isfile(path) else None