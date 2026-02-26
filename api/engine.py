import io
import qrcode
from PIL import Image


def build_qr(text: str, logo_bytes: bytes = None) -> bytes:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    if logo_bytes:
        logo_img = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")

        qr_w, qr_h = img.size
        logo_size = int(qr_w * 0.25)
        logo_img.thumbnail((logo_size, logo_size), Image.LANCZOS)
        lw, lh = logo_img.size

        pos = ((qr_w - lw) // 2, (qr_h - lh) // 2)
        img.paste(Image.new("RGB", (lw, lh), "white"), pos)
        img.paste(logo_img, pos, mask=logo_img)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()