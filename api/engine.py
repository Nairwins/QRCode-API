import io
import qrcode
from PIL import Image, ImageDraw


def _recolor_png(png_path, color: tuple, size: int, rotate: int = 0) -> Image.Image:
    """Load a PNG, recolor all visible pixels, resize, and optionally rotate."""
    img = Image.open(png_path).convert("RGBA")
    img = img.resize((size, size), Image.LANCZOS)

    r, g, b = color
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            pr, pg, pb, pa = pixels[x, y]
            if pa > 10:
                pixels[x, y] = (r, g, b, pa)

    if rotate:
        img = img.rotate(-rotate, expand=False)

    return img


def _draw_eyes(img: Image.Image, qr: qrcode.QRCode,
               bg_color: tuple,
               outer_color: tuple, outer_png,
               inner_color: tuple, inner_png):
    draw = ImageDraw.Draw(img)
    box    = qr.box_size
    border = qr.border
    size   = qr.modules_count

    # (origin_x, origin_y, outer_rotation)
    eye_configs = [
        (border,            border,            0),    # top-left
        (border + size - 7, border,            90),   # top-right
        (border,            border + size - 7, 270),  # bottom-left
    ]

    for ox, oy, rotation in eye_configs:
        px, py = ox * box, oy * box
        eye_px = 7 * box

        draw.rectangle([px, py, px + eye_px - 1, py + eye_px - 1], fill=bg_color)

        if outer_png:
            outer_img = _recolor_png(outer_png, outer_color, eye_px, rotate=rotation)
            img.paste(outer_img, (px, py), mask=outer_img)
        else:
            draw.rectangle([px, py, px + eye_px - 1, py + eye_px - 1], fill=outer_color)
            draw.rectangle([px + box, py + box, px + 6*box - 1, py + 6*box - 1], fill=bg_color)

        inner_px = 3 * box
        ix = px + 2 * box
        iy = py + 2 * box

        if inner_png:
            inner_img = _recolor_png(inner_png, inner_color, inner_px)
            img.paste(inner_img, (ix, iy), mask=inner_img)
        else:
            draw.rectangle([ix, iy, ix + inner_px - 1, iy + inner_px - 1], fill=inner_color)


def build_qr(
    text: str,
    logo_bytes: bytes = None,
    body_color:      tuple = (0, 0, 0),
    bg_color:        tuple = (255, 255, 255),
    outer_eye_color: tuple = (0, 0, 0),
    inner_eye_color: tuple = (0, 0, 0),
    outer_png=None,
    inner_png=None,
) -> bytes:
    def to_hex(rgb): return "#{:02x}{:02x}{:02x}".format(*rgb)

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color=to_hex(body_color),
        back_color=to_hex(bg_color),
    ).convert("RGB")

    _draw_eyes(img, qr, bg_color, outer_eye_color, outer_png, inner_eye_color, inner_png)

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