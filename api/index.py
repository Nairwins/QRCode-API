import io
from pathlib import Path
import qrcode
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from PIL import Image

app = FastAPI()

ICONS_DIR = Path(__file__).parent / "icons"

@app.post("/qr")
async def generate_qr(
    text: str = Query(..., description="Text to encode"),
    logo: UploadFile = File(None, description="Custom logo image"),
    default_icon: str = Query(None, description="Use a default icon by name, e.g. 'gold'"),
):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Resolve logo source: custom upload takes priority over default icon
    logo_bytes = None
    if logo:
        logo_bytes = await logo.read()
    elif default_icon:
        icon_path = ICONS_DIR / f"{default_icon}.png"
        if not icon_path.exists():
            raise HTTPException(status_code=404, detail=f"Icon '{default_icon}' not found")
        logo_bytes = icon_path.read_bytes()

    if logo_bytes:
        logo_img = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")

        qr_w, qr_h = img.size
        logo_size = int(qr_w * 0.25)
        logo_img.thumbnail((logo_size, logo_size), Image.LANCZOS)
        lw, lh = logo_img.size

        # White bg exact same size as logo
        white_bg = Image.new("RGB", (lw, lh), "white")
        pos = ((qr_w - lw) // 2, (qr_h - lh) // 2)
        img.paste(white_bg, pos)
        img.paste(logo_img, pos, mask=logo_img)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)