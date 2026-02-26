import io
import qrcode
from PIL import Image, ImageDraw


def _draw_eyes(img: Image.Image, qr: qrcode.QRCode,
               bg_color: tuple, outer_color: tuple, inner_color: tuple):
    """Repaint the 3 finder pattern eyes with custom colors."""
    draw = ImageDraw.Draw(img)
    box = qr.box_size
    border = qr.border
    size = qr.modules_count  # actual QR data size (no border)

    # The 3 eye top-left corners in module coordinates (relative to full image)
    eye_origins = [
        (border,          border),           # top-left
        (border + size - 7, border),         # top-right
        (border,          border + size - 7) # bottom-left
    ]

    for ox, oy in eye_origins:
        # Convert to pixels
        px, py = ox * box, oy * box

        # 1. Fill full 7x7 with outer color
        draw.rectangle([px, py, px + 7*box - 1, py + 7*box - 1], fill=outer_color)

        # 2. Hollow out 5x5 inside with bg color
        draw.rectangle([px + box, py + box, px + 6*box - 1, py + 6*box - 1], fill=bg_color)

        # 3. Fill 3x3 center with inner color
        draw.rectangle([px + 2*box, py + 2*box, px + 5*box - 1, py + 5*box - 1], fill=inner_color)


def build_qr(
    text: str,
    logo_bytes: bytes = None,
    body_color: tuple = (0, 0, 0),
    bg_color: tuple = (255, 255, 255),
    outer_eye_color: tuple = (0, 0, 0),
    inner_eye_color: tuple = (0, 0, 0),
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

    _draw_eyes(img, qr, bg_color, outer_eye_color, inner_eye_color)

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