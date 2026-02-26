import io
import qrcode
from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import Response
from PIL import Image

app = FastAPI()

@app.post("/qr")
async def generate_qr(
    text: str = Query(..., description="Text to encode"),
    logo: UploadFile = File(None, description="Optional logo image"),
):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    if logo:
        logo_img = Image.open(io.BytesIO(await logo.read())).convert("RGBA")

        # Resize logo to 25% of QR code
        qr_w, qr_h = img.size
        logo_size = int(qr_w * 0.25)
        logo_img.thumbnail((logo_size, logo_size), Image.LANCZOS)
        lw, lh = logo_img.size

        # White background to kill dots under logo
        padding = 10
        white_bg = Image.new("RGB", (lw + padding * 2, lh + padding * 2), "white")
        bg_pos = ((qr_w - white_bg.width) // 2, (qr_h - white_bg.height) // 2)
        img.paste(white_bg, bg_pos)

        # Center logo on top
        pos = ((qr_w - lw) // 2, (qr_h - lh) // 2)
        img.paste(logo_img, pos, mask=logo_img)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)