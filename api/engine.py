import io
import math
import qrcode
from PIL import Image, ImageDraw

SUPERSAMPLE = 8  # draw at 8x, downscale for crisp anti-aliasing


# ── Dot drawer ────────────────────────────────────────────────────────────────

def _draw_module(draw, x, y, box, color, style, matrix, row, col):
    x1, y1 = x + box, y + box
    cx, cy  = x + box / 2, y + box / 2
    pad     = box * 0.08

    def has(r, c):
        if r < 0 or c < 0 or r >= len(matrix) or c >= len(matrix[0]):
            return False
        return matrix[r][c]

    if style == "square":
        draw.rectangle([x, y, x1, y1], fill=color)

    elif style == "dot":
        draw.ellipse([x + pad, y + pad, x1 - pad, y1 - pad], fill=color)

    elif style == "block":
        gap = box * 0.05
        draw.rectangle([x + gap, y + gap, x1 - gap, y1 - gap], fill=color)

    elif style == "rounded":
        r = box * 0.30
        draw.rounded_rectangle([x + pad, y + pad, x1 - pad, y1 - pad], radius=r, fill=color)

    elif style == "diamond":
        half = box / 2 - pad
        draw.polygon([(cx, cy - half), (cx + half, cy), (cx, cy + half), (cx - half, cy)], fill=color)

    elif style == "smooth":
        draw.ellipse([x + pad, y + pad, x1 - pad, y1 - pad], fill=color)
        if has(row - 1, col): draw.rectangle([x + pad, y,  x1 - pad, cy], fill=color)
        if has(row + 1, col): draw.rectangle([x + pad, cy, x1 - pad, y1], fill=color)
        if has(row, col - 1): draw.rectangle([x,  y + pad, cx, y1 - pad], fill=color)
        if has(row, col + 1): draw.rectangle([cx, y + pad, x1, y1 - pad], fill=color)

    elif style == "vertical":
        draw.ellipse([x + pad, y + pad, x1 - pad, y1 - pad], fill=color)
        if has(row - 1, col): draw.rectangle([x + pad, y,  x1 - pad, cy], fill=color)
        if has(row + 1, col): draw.rectangle([x + pad, cy, x1 - pad, y1], fill=color)

    elif style == "horizontal":
        draw.ellipse([x + pad, y + pad, x1 - pad, y1 - pad], fill=color)
        if has(row, col - 1): draw.rectangle([x,  y + pad, cx, y1 - pad], fill=color)
        if has(row, col + 1): draw.rectangle([cx, y + pad, x1, y1 - pad], fill=color)

    elif style == "aura":
        half = box / 2 - pad
        draw.polygon([(cx, cy - half), (cx + half, cy), (cx, cy + half), (cx - half, cy)], fill=color)
        bw = half * 0.75
        if has(row - 1, col):
            draw.polygon([(cx-bw, cy), (cx+bw, cy), (cx+bw, y), (cx, y-1), (cx-bw, y)], fill=color)
        if has(row + 1, col):
            draw.polygon([(cx-bw, cy), (cx+bw, cy), (cx+bw, y1), (cx, y1+1), (cx-bw, y1)], fill=color)
        if has(row, col - 1):
            draw.polygon([(cx, cy-bw), (cx, cy+bw), (x, cy+bw), (x-1, cy), (x, cy-bw)], fill=color)
        if has(row, col + 1):
            draw.polygon([(cx, cy-bw), (cx, cy+bw), (x1, cy+bw), (x1+1, cy), (x1, cy-bw)], fill=color)
        if has(row - 1, col) and has(row, col - 1): draw.rectangle([x,        y,        cx, cy], fill=color)
        if has(row - 1, col) and has(row, col + 1): draw.rectangle([cx,       y,        x1, cy], fill=color)
        if has(row + 1, col) and has(row, col - 1): draw.rectangle([x,        cy,       cx, y1], fill=color)
        if has(row + 1, col) and has(row, col + 1): draw.rectangle([cx,       cy,       x1, y1], fill=color)

    else:
        draw.rectangle([x, y, x1, y1], fill=color)


# ── Built-in eye drawers ──────────────────────────────────────────────────────

def _draw_outer_builtin(draw, px, py, eye_px, box, color, bg, style):
    """Draw outer eye frame with a built-in style (no PNG needed)."""
    if style == "square":
        draw.rectangle([px, py, px + eye_px - 1, py + eye_px - 1], fill=color)
        draw.rectangle([px + box, py + box, px + 6*box - 1, py + 6*box - 1], fill=bg)

    elif style == "rounded":
        r = box * 1.2
        draw.rounded_rectangle([px, py, px + eye_px - 1, py + eye_px - 1], radius=r, fill=color)
        draw.rounded_rectangle([px + box, py + box, px + 6*box - 1, py + 6*box - 1], radius=r * 0.6, fill=bg)

    elif style == "circle":
        draw.ellipse([px, py, px + eye_px - 1, py + eye_px - 1], fill=color)
        draw.ellipse([px + box, py + box, px + 6*box - 1, py + 6*box - 1], fill=bg)

    elif style == "dots":
        # Frame made of 16 dots around the border
        dot_r = box * 0.4
        positions = []
        for i in range(7):
            positions += [(px + i*box, py), (px + i*box, py + 6*box)]
        for i in range(1, 6):
            positions += [(px, py + i*box), (px + 6*box, py + i*box)]
        for (dx, dy) in positions:
            draw.ellipse([dx + dot_r*0.3, dy + dot_r*0.3,
                          dx + box - dot_r*0.3, dy + box - dot_r*0.3], fill=color)

    else:  # fallback square
        draw.rectangle([px, py, px + eye_px - 1, py + eye_px - 1], fill=color)
        draw.rectangle([px + box, py + box, px + 6*box - 1, py + 6*box - 1], fill=bg)


def _draw_inner_builtin(draw, ix, iy, inner_px, box, color, style):
    """Draw inner eye dot with a built-in style (no PNG needed)."""
    if style == "square":
        draw.rectangle([ix, iy, ix + inner_px - 1, iy + inner_px - 1], fill=color)

    elif style == "rounded":
        r = box * 0.6
        draw.rounded_rectangle([ix, iy, ix + inner_px - 1, iy + inner_px - 1], radius=r, fill=color)

    elif style == "circle":
        draw.ellipse([ix, iy, ix + inner_px - 1, iy + inner_px - 1], fill=color)

    elif style == "diamond":
        cx = ix + inner_px / 2
        cy = iy + inner_px / 2
        half = inner_px / 2
        draw.polygon([(cx, iy), (ix + inner_px, cy), (cx, iy + inner_px), (ix, cy)], fill=color)

    else:
        draw.rectangle([ix, iy, ix + inner_px - 1, iy + inner_px - 1], fill=color)


# ── Gradient ──────────────────────────────────────────────────────────────────

def _make_gradient_map(size, color1, color2, mode):
    w, h = size
    gradient = Image.new("RGB", (w, h))
    px = gradient.load()
    for y in range(h):
        for x in range(w):
            if mode == "horizontal": t = x / (w - 1)
            elif mode == "vertical": t = y / (h - 1)
            elif mode == "diagonal": t = (x + y) / (w + h - 2)
            elif mode == "center":
                cx2, cy2 = w / 2, h / 2
                t = min(math.sqrt((x-cx2)**2 + (y-cy2)**2) / math.sqrt(cx2**2 + cy2**2), 1.0)
            else: t = 0
            r = int(color1[0] + (color2[0] - color1[0]) * t)
            g = int(color1[1] + (color2[1] - color1[1]) * t)
            b = int(color1[2] + (color2[2] - color1[2]) * t)
            px[x, y] = (r, g, b)
    return gradient


def _apply_gradient(img, color1, color2, mode, bg_color):
    gradient = _make_gradient_map(img.size, color1, color2, mode)
    result = img.copy()
    src = img.load(); grad = gradient.load(); out = result.load()
    br, bg, bb = bg_color
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = src[x, y]
            if abs(r-br) < 40 and abs(g-bg) < 40 and abs(b-bb) < 40: continue
            out[x, y] = grad[x, y]
    return result


# ── Eye helpers ───────────────────────────────────────────────────────────────

def _recolor_png(png_path, color, size, rotate=0):
    img = Image.open(png_path).convert("RGBA")
    img = img.resize((size, size), Image.LANCZOS)
    r, g, b = color
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            pr, pg, pb, pa = pixels[x, y]
            if pa > 10: pixels[x, y] = (r, g, b, pa)
    if rotate: img = img.rotate(-rotate, expand=False)
    return img


def _eye_modules(qr):
    border = qr.border
    size   = qr.modules_count
    coords = set()
    for origin_r, origin_c in [
        (border,            border),
        (border,            border + size - 7),
        (border + size - 7, border),
    ]:
        for dr in range(7):
            for dc in range(7):
                coords.add((origin_r + dr, origin_c + dc))
    return coords


def _draw_eyes(img, qr, bg_color,
               outer_color, outer_png, outer_builtin,
               inner_color, inner_png, inner_builtin):
    draw   = ImageDraw.Draw(img)
    box    = qr.box_size
    border = qr.border
    size   = qr.modules_count

    eye_configs = [
        (border,            border,            0),
        (border + size - 7, border,            90),
        (border,            border + size - 7, 270),
    ]

    for ox, oy, rotation in eye_configs:
        px, py = ox * box, oy * box
        eye_px = 7 * box
        inner_px = 3 * box
        ix = px + 2 * box
        iy = py + 2 * box

        # Clear zone
        draw.rectangle([px, py, px + eye_px - 1, py + eye_px - 1], fill=bg_color)

        # Outer eye
        if outer_png:
            outer_img = _recolor_png(outer_png, outer_color, eye_px, rotate=rotation)
            img.paste(outer_img, (px, py), mask=outer_img)
        else:
            _draw_outer_builtin(draw, px, py, eye_px, box, outer_color, bg_color, outer_builtin)

        # Inner eye
        if inner_png:
            inner_img = _recolor_png(inner_png, inner_color, inner_px)
            img.paste(inner_img, (ix, iy), mask=inner_img)
        else:
            _draw_inner_builtin(draw, ix, iy, inner_px, box, inner_color, inner_builtin)


# ── Main build ────────────────────────────────────────────────────────────────

def build_qr(
    text:            str,
    logo_bytes:      bytes = None,
    body_color:      tuple = (0, 0, 0),
    bg_color:        tuple = (255, 255, 255),
    outer_eye_color: tuple = (0, 0, 0),
    inner_eye_color: tuple = (0, 0, 0),
    outer_png=None,
    inner_png=None,
    outer_builtin:   str   = "square",
    inner_builtin:   str   = "square",
    gradient_color:  tuple = None,
    gradient_type:   str   = None,
    dot_style:       str   = "square",
) -> bytes:
    def to_hex(rgb): return "#{:02x}{:02x}{:02x}".format(*rgb)

    BOX   = 20
    S     = SUPERSAMPLE
    box_s = BOX * S

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_s,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    matrix     = qr.get_matrix()
    total_size = len(matrix) * box_s
    eye_coords = _eye_modules(qr)

    img_big  = Image.new("RGB", (total_size, total_size), bg_color)
    draw_big = ImageDraw.Draw(img_big)

    for row, row_data in enumerate(matrix):
        for col, on in enumerate(row_data):
            if not on or (row, col) in eye_coords:
                continue
            _draw_module(draw_big, col * box_s, row * box_s, box_s, body_color, dot_style, matrix, row, col)

    final_size = len(matrix) * BOX
    img = img_big.resize((final_size, final_size), Image.LANCZOS)

    if gradient_color and gradient_type:
        img = _apply_gradient(img, body_color, gradient_color, gradient_type, bg_color)

    qr.box_size = BOX
    _draw_eyes(img, qr, bg_color,
               outer_eye_color, outer_png, outer_builtin,
               inner_eye_color, inner_png, inner_builtin)

    if logo_bytes:
        logo_img = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
        qr_w, qr_h = img.size
        logo_size = int(qr_w * 0.25)
        logo_img.thumbnail((logo_size, logo_size), Image.LANCZOS)
        lw, lh = logo_img.size
        pos = ((qr_w - lw) // 2, (qr_h - lh) // 2)
        img.paste(Image.new("RGB", (lw, lh), to_hex(bg_color)), pos)
        img.paste(logo_img, pos, mask=logo_img)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()