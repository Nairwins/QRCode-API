DEFAULT_FG = "#000000"
DEFAULT_BG = "#ffffff"
DEFAULT_SIZE = 10
DEFAULT_BORDER = 4
DEFAULT_GRADIENT = "horizontal"
DEFAULT_SHAPE = "square"

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
    "square",           # classic filled square
    "circle",           # full circle filling the cell
    "dot",              # small circle (60% of cell)
    "rounded",          # square with rounded corners
    "smooth",           # square with very smooth/pill rounded corners
    "diamond",          # rotated 45° square
    "diamond_small",    # smaller diamond with padding
    "star4",            # 4-pointed star
    "star5",            # 5-pointed star (classic)
    "cross",            # plus / cross shape
    "heart",            # heart shape
    "triangle_up",      # upward triangle
    "triangle_down",    # downward triangle
    "hexagon",          # flat-top hexagon
    "octagon",          # 8-sided shape
    "arrow_right",      # arrow pointing right
    "vertical_line",    # tall thin bar
    "horizontal_line",  # wide thin bar
    "x_shape",          # X / times shape
    "ring",             # hollow circle / donut
    "bars",             # three horizontal mini-bars
]

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

    hex_val = value if value.startswith("#") else f"#{value}"
    if hex_val.startswith("#") and len(hex_val) in [4, 7]:
        try:
            int(hex_val[1:], 16)
            return hex_val
        except ValueError:
            pass

    return fallback