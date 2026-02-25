from PIL import Image, ImageDraw
import qrcode
import math
import cairosvg
from io import BytesIO
from assets import resolve_color, DEFAULT_BG, DEFAULT_FG, INNER_DIR, OUTER_DIR, get_svg_path


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


def render_svg(svg_path: str, width: int, height: int, color: str) -> Image.Image:
    with open(svg_path, "r") as f:
        svg_content = f.read()

    svg_content = svg_content.replace("currentColor", color)

    png_bytes = cairosvg.svg2png(
        bytestring=svg_content.encode(),
        output_width=width,
        output_height=height,
    )

    return Image.open(BytesIO(png_bytes)).convert("RGBA")


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
        draw.ellipse([x1+pad, y1+pad, x2-pad, y2-pad], fill=color)
    elif shape == "rounded":
        draw.rounded_rectangle([x1, y1, x2, y2], radius=box_size // 3, fill=color)
    elif shape == "smooth":
        draw.rounded_rectangle([x1, y1, x2, y2], radius=int(box_size * 0.45), fill=color)
    elif shape == "diamond":
        draw.polygon([(cx, y1), (x2, cy), (cx, y2), (x1, cy)], fill=color)
    elif shape == "diamond_small":
        pad = box_size // 6
        draw.polygon([(cx, y1+pad), (x2-pad, cy), (cx, y2-pad), (x1+pad, cy)], fill=color)
    elif shape == "star4":
        q = box_size // 4
        draw.polygon([
            (cx, y1), (cx+q*0.5, cy-q*0.5),
            (x2, cy), (cx+q*0.5, cy+q*0.5),
            (cx, y2), (cx-q*0.5, cy+q*0.5),
            (x1, cy), (cx-q*0.5, cy-q*0.5),
        ], fill=color)
    elif shape == "star5":
        outer_r, inner_r = r, r * 0.4
        pts = []
        for i in range(10):
            a = math.radians(-90 + i * 36)
            ri = outer_r if i % 2 == 0 else inner_r
            pts.append((cx + ri * math.cos(a), cy + ri * math.sin(a)))
        draw.polygon(pts, fill=color)
    elif shape == "cross":
        t = box_size // 3
        draw.rectangle([x1, y1+t, x2, y2-t], fill=color)
        draw.rectangle([x1+t, y1, x2-t, y2], fill=color)
    elif shape == "heart":
        scale = (box_size / 2) / 10
        pts = []
        for i in range(360):
            a = math.radians(i)
            hx = 16 * math.sin(a) ** 3
            hy = -(13 * math.cos(a) - 5 * math.cos(2*a) - 2 * math.cos(3*a) - math.cos(4*a))
            pts.append((cx + hx * scale * 0.6, cy + hy * scale * 0.6 + box_size * 0.05))
        draw.polygon(pts, fill=color)
    elif shape == "triangle_up":
        draw.polygon([(cx, y1), (x2, y2), (x1, y2)], fill=color)
    elif shape == "triangle_down":
        draw.polygon([(x1, y1), (x2, y1), (cx, y2)], fill=color)
    elif shape == "hexagon":
        pts = [(cx + r*math.cos(math.radians(i*60-30)), cy + r*math.sin(math.radians(i*60-30))) for i in range(6)]
        draw.polygon(pts, fill=color)
    elif shape == "octagon":
        pts = [(cx + r*math.cos(math.radians(i*45-22.5)), cy + r*math.sin(math.radians(i*45-22.5))) for i in range(8)]
        draw.polygon(pts, fill=color)
    elif shape == "arrow_right":
        mid = box_size // 2
        tip = box_size // 3
        draw.polygon([
            (x1, y1+tip), (x1+mid, y1+tip), (x1+mid, y1),
            (x2, cy),
            (x1+mid, y2), (x1+mid, y2-tip), (x1, y2-tip),
        ], fill=color)
    elif shape == "vertical_line":
        pad = box_size // 3
        draw.rectangle([x1+pad, y1, x2-pad, y2], fill=color)
    elif shape == "horizontal_line":
        pad = box_size // 3
        draw.rectangle([x1, y1+pad, x2, y2-pad], fill=color)
    elif shape == "x_shape":
        t = max(2, box_size // 4)
        draw.polygon([
            (x1, y1), (x1+t, y1), (cx, cy-t*0.5),
            (x2-t, y1), (x2, y1), (cx+t*0.5, cy),
            (x2, y2), (x2-t, y2), (cx, cy+t*0.5),
            (x1+t, y2), (x1, y2), (cx-t*0.5, cy),
        ], fill=color)
    elif shape == "ring":
        draw.ellipse([x1, y1, x2, y2], fill=color)
        pad = max(2, box_size // 4)
        draw.ellipse([x1+pad, y1+pad, x2-pad, y2-pad], fill=(0, 0, 0, 0))
    elif shape == "bars":
        bar_h = max(1, box_size // 5)
        gap = max(1, box_size // 8)
        total = 3 * bar_h + 2 * gap
        sy = y1 + (box_size - total) // 2
        for i in range(3):
            by = sy + i * (bar_h + gap)
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
                dist = ((x-cx)**2 + (y-cy)**2) ** 0.5
                t = dist / ((cx**2 + cy**2) ** 0.5)
            elif gradient_type == "center_reverse":
                cx, cy = width / 2, height / 2
                dist = ((x-cx)**2 + (y-cy)**2) ** 0.5
                t = 1 - dist / ((cx**2 + cy**2) ** 0.5)
            else:
                t = x / (width - 1)

            t = max(0.0, min(1.0, t))
            pixels[x, y] = (
                int(r1 + (r2 - r1) * t),
                int(g1 + (g2 - g1) * t),
                int(b1 + (b2 - b1) * t),
            )
    return gradient


def draw_eyes(img, box_size, border, modules_count, outer_color, inner_color, bg_color, outer_svg=None, inner_svg=None):
    draw = ImageDraw.Draw(img)

    eye_positions = [
        (0, 0),
        (0, modules_count - 7),
        (modules_count - 7, 0),
    ]

    outer_size = 7 * box_size
    inner_size = 3 * box_size

    for (row, col) in eye_positions:
        x = (col + border) * box_size
        y = (row + border) * box_size

        # Outer eye
        if outer_svg:
            svg_img = render_svg(outer_svg, outer_size, outer_size, outer_color)
            img.paste(svg_img, (x, y), svg_img)
        else:
            draw.rectangle([x, y, x+outer_size-1, y+outer_size-1], fill=hex_to_rgb(outer_color))

        # White gap between outer and inner
        draw.rectangle(
            [x+box_size, y+box_size, x+6*box_size-1, y+6*box_size-1],
            fill=bg_color,
        )

        # Inner eye
        ix = x + 2 * box_size
        iy = y + 2 * box_size

        if inner_svg:
            svg_img = render_svg(inner_svg, inner_size, inner_size, inner_color)
            img.paste(svg_img, (ix, iy), svg_img)
        else:
            draw.rectangle([ix, iy, ix+inner_size-1, iy+inner_size-1], fill=hex_to_rgb(inner_color))


def build_qr_image(
    data, size, border, fg_color, bg_color,
    gradient_color=None, gradient_type="horizontal",
    eye_outer=None, eye_inner=None,
    dot_shape="square",
    eye_outer_shape=None, eye_inner_shape=None,
) -> BytesIO:
    fg = resolve_color(fg_color, DEFAULT_FG)
    bg = resolve_color(bg_color, DEFAULT_BG)
    grad = resolve_color(gradient_color, None) if gradient_color else None
    outer_color = resolve_color(eye_outer, fg) if eye_outer else fg
    inner_color = resolve_color(eye_inner, fg) if eye_inner else fg
    bg_rgb = hex_to_rgb(bg)

    outer_svg = get_svg_path(OUTER_DIR, eye_outer_shape) if eye_outer_shape else None
    inner_svg = get_svg_path(INNER_DIR, eye_inner_shape) if eye_inner_shape else None

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
    total = n * size

    if grad:
        mask_img = Image.new("L", (total, total), 0)
        mask_draw = ImageDraw.Draw(mask_img)

        for row in range(n):
            for col in range(n):
                if matrix[row][col] and not is_eye_module(row - border, col - border, n - 2 * border):
                    draw_dot(mask_draw, col * size, row * size, size, dot_shape, 255)

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
                    draw_dot(draw, col * size, row * size, size, dot_shape, hex_to_rgb(fg))

    draw_eyes(
        final_img, size, border,
        n - 2 * border,
        outer_color, inner_color, bg_rgb,
        outer_svg=outer_svg,
        inner_svg=inner_svg,
    )

    buffer = BytesIO()
    final_img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer