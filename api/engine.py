from PIL import Image, ImageDraw
import qrcode
import math
from io import BytesIO
try:
    from api.assets import resolve_color, DEFAULT_BG, DEFAULT_FG
except ImportError:
    from assets import resolve_color, DEFAULT_BG, DEFAULT_FG


def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def is_eye_module(row, col, n):
    if row < 7 and col < 7:
        return True
    if row < 7 and col >= n - 7:
        return True
    if row >= n - 7 and col < 7:
        return True
    return False


def draw_dot(draw, x, y, box_size, shape, color):
    x1, y1 = x, y
    x2, y2 = x + box_size - 1, y + box_size - 1
    cx = x + box_size / 2
    cy = y + box_size / 2
    r = box_size / 2

    if shape == "square":
        draw.rectangle([x1, y1, x2, y2], fill=color)

    elif shape == "circle":
        draw.ellipse([x1, y1, x2, y2], fill=color)

    elif shape == "dot":
        pad = max(1, box_size // 5)
        draw.ellipse([x1 + pad, y1 + pad, x2 - pad, y2 - pad], fill=color)

    elif shape == "rounded":
        radius = box_size // 3
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=color)

    elif shape == "smooth":
        radius = int(box_size * 0.45)
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=color)

    elif shape == "diamond":
        points = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
        draw.polygon(points, fill=color)

    elif shape == "diamond_small":
        pad = box_size // 6
        points = [
            (cx, y1 + pad),
            (x2 - pad, cy),
            (cx, y2 - pad),
            (x1 + pad, cy),
        ]
        draw.polygon(points, fill=color)

    elif shape == "star4":
        q = box_size // 4
        points = [
            (cx, y1),
            (cx + q * 0.5, cy - q * 0.5),
            (x2, cy),
            (cx + q * 0.5, cy + q * 0.5),
            (cx, y2),
            (cx - q * 0.5, cy + q * 0.5),
            (x1, cy),
            (cx - q * 0.5, cy - q * 0.5),
        ]
        draw.polygon(points, fill=color)

    elif shape == "star5":
        outer_r = r
        inner_r = r * 0.4
        points = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            radius_i = outer_r if i % 2 == 0 else inner_r
            points.append((cx + radius_i * math.cos(angle), cy + radius_i * math.sin(angle)))
        draw.polygon(points, fill=color)

    elif shape == "cross":
        third = box_size // 3
        draw.rectangle([x1, y1 + third, x2, y2 - third], fill=color)
        draw.rectangle([x1 + third, y1, x2 - third, y2], fill=color)

    elif shape == "heart":
        hw = box_size / 2
        scale = hw / 10
        points = []
        for i in range(360):
            angle = math.radians(i)
            hx = 16 * math.sin(angle) ** 3
            hy = -(13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle))
            points.append((cx + hx * scale * 0.6, cy + hy * scale * 0.6 + box_size * 0.05))
        draw.polygon(points, fill=color)

    elif shape == "triangle_up":
        points = [(cx, y1), (x2, y2), (x1, y2)]
        draw.polygon(points, fill=color)

    elif shape == "triangle_down":
        points = [(x1, y1), (x2, y1), (cx, y2)]
        draw.polygon(points, fill=color)

    elif shape == "hexagon":
        points = []
        for i in range(6):
            angle = math.radians(i * 60 - 30)
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        draw.polygon(points, fill=color)

    elif shape == "octagon":
        points = []
        for i in range(8):
            angle = math.radians(i * 45 - 22.5)
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        draw.polygon(points, fill=color)

    elif shape == "arrow_right":
        mid = box_size // 2
        tip = box_size // 3
        points = [
            (x1, y1 + tip),
            (x1 + mid, y1 + tip),
            (x1 + mid, y1),
            (x2, cy),
            (x1 + mid, y2),
            (x1 + mid, y2 - tip),
            (x1, y2 - tip),
        ]
        draw.polygon(points, fill=color)

    elif shape == "vertical_line":
        pad = box_size // 3
        draw.rectangle([x1 + pad, y1, x2 - pad, y2], fill=color)

    elif shape == "horizontal_line":
        pad = box_size // 3
        draw.rectangle([x1, y1 + pad, x2, y2 - pad], fill=color)

    elif shape == "x_shape":
        t = max(2, box_size // 4)
        points1 = [
            (x1, y1), (x1 + t, y1), (cx, cy - t * 0.5),
            (x2 - t, y1), (x2, y1), (cx + t * 0.5, cy),
            (x2, y2), (x2 - t, y2), (cx, cy + t * 0.5),
            (x1 + t, y2), (x1, y2), (cx - t * 0.5, cy),
        ]
        draw.polygon(points1, fill=color)

    elif shape == "ring":
        draw.ellipse([x1, y1, x2, y2], fill=color)
        pad = max(2, box_size // 4)
        bg = color  # will be overwritten below — caller handles bg
        draw.ellipse([x1 + pad, y1 + pad, x2 - pad, y2 - pad], fill=(0, 0, 0, 0))

    elif shape == "bars":
        bar_h = max(1, box_size // 5)
        gap = max(1, box_size // 8)
        total = 3 * bar_h + 2 * gap
        start_y = y1 + (box_size - total) // 2
        for i in range(3):
            by = start_y + i * (bar_h + gap)
            draw.rectangle([x1, by, x2, by + bar_h], fill=color)

    else:
        draw.rectangle([x1, y1, x2, y2], fill=color)


def create_gradient(width, height, color1, color2, gradient_type):
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
    dot_shape: str = "square",
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

    matrix = qr.get_matrix()
    n = len(matrix)
    img_size = (n + 2 * border) * size  # border already embedded in matrix via QRCode border param
    # Actually qr.get_matrix() includes the quiet zone set by `border`
    # so total size is just n * size
    total = n * size

    bg_rgb = hex_to_rgb(bg)
    fg_rgb = hex_to_rgb(fg)

    if grad:
        # Draw mask with custom shapes
        mask_img = Image.new("L", (total, total), 0)
        mask_draw = ImageDraw.Draw(mask_img)

        for row in range(n):
            for col in range(n):
                if matrix[row][col] and not is_eye_module(row - border, col - border, n - 2 * border):
                    x = col * size
                    y = row * size
                    draw_dot(mask_draw, x, y, size, dot_shape, 255)

        result = Image.new("RGB", (total, total), bg_rgb)
        gradient = create_gradient(total, total, fg, grad, gradient_type)
        result.paste(gradient, (0, 0), mask_img)
        final_img = result

    else:
        final_img = Image.new("RGB", (total, total), bg_rgb)
        draw = ImageDraw.Draw(final_img)

        for row in range(n):
            for col in range(n):
                if matrix[row][col] and not is_eye_module(row - border, col - border, n - 2 * border):
                    x = col * size
                    y = row * size
                    draw_dot(draw, x, y, size, dot_shape, fg_rgb)

    draw_eyes(
        final_img, size, border,
        n - 2 * border,
        hex_to_rgb(outer),
        hex_to_rgb(inner),
        bg_rgb,
    )

    buffer = BytesIO()
    final_img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer