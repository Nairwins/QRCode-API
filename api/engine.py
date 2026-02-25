from PIL import Image, ImageDraw
import qrcode
from io import BytesIO
from api.assets import resolve_color, DEFAULT_BG, DEFAULT_FG


def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient(width: int, height: int, color1: str, color2: str, gradient_type: str) -> Image.Image:
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)

    gradient = Image.new("RGB", (width, height))
    pixels = gradient.load()

    for y in range(height):
        for x in range(width):
            if gradient_type == "horizontal":
                t = x / (width - 1)
            elif gradient_type == "vertical":
                t = y / (height - 1)
            elif gradient_type == "diagonal":
                t = (x + y) / (width + height - 2)
            elif gradient_type == "diagonal_reverse":
                t = (x + (height - y)) / (width + height - 2)
            elif gradient_type == "center":
                cx, cy = width / 2, height / 2
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                max_dist = (cx ** 2 + cy ** 2) ** 0.5
                t = dist / max_dist
            elif gradient_type == "center_reverse":
                cx, cy = width / 2, height / 2
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                max_dist = (cx ** 2 + cy ** 2) ** 0.5
                t = 1 - (dist / max_dist)
            else:
                t = x / (width - 1)

            t = max(0.0, min(1.0, t))
            pixels[x, y] = (
                int(r1 + (r2 - r1) * t),
                int(g1 + (g2 - g1) * t),
                int(b1 + (b2 - b1) * t),
            )

    return gradient


def draw_eyes(img, box_size, border, modules_count, outer_color, inner_color, bg_color):
    draw = ImageDraw.Draw(img)

    eye_positions = [
        (0, 0),
        (0, modules_count - 7),
        (modules_count - 7, 0),
    ]

    for (row, col) in eye_positions:
        x = (col + border) * box_size
        y = (row + border) * box_size

        draw.rectangle([x, y, x + 7 * box_size - 1, y + 7 * box_size - 1], fill=outer_color)
        draw.rectangle([x + box_size, y + box_size, x + 6 * box_size - 1, y + 6 * box_size - 1], fill=bg_color)
        draw.rectangle([x + 2 * box_size, y + 2 * box_size, x + 5 * box_size - 1, y + 5 * box_size - 1], fill=inner_color)


def build_qr_image(
    data: str,
    size: int,
    border: int,
    fg_color: str,
    bg_color: str,
    gradient_color: str = None,
    gradient_type: str = "horizontal",
    eye_outer: str = None,
    eye_inner: str = None,
) -> BytesIO:
    fg = resolve_color(fg_color, DEFAULT_FG)
    bg = resolve_color(bg_color, DEFAULT_BG)
    grad = resolve_color(gradient_color, None) if gradient_color else None
    outer = resolve_color(eye_outer, fg) if eye_outer else fg
    inner = resolve_color(eye_inner, fg) if eye_inner else fg

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    modules_count = qr.modules_count

    if grad:
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        width, height = qr_img.size

        result = Image.new("RGB", (width, height), hex_to_rgb(bg))
        gradient = create_gradient(width, height, fg, grad, gradient_type)
        mask = qr_img.convert("L").point(lambda p: 255 if p < 128 else 0)
        result.paste(gradient, (0, 0), mask)
        final_img = result
    else:
        final_img = qr.make_image(fill_color=fg, back_color=bg).convert("RGB")

    draw_eyes(final_img, size, border, modules_count, hex_to_rgb(outer), hex_to_rgb(inner), hex_to_rgb(bg))

    buffer = BytesIO()
    final_img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer