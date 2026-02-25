from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import qrcode
from io import BytesIO

app = FastAPI()

@app.get("/")
def root():
    return {"message": "QR Code Generator API is running!"}

@app.get("/generate")
def generate_qr(
    data: str = Query(..., description="Text or URL to encode"),
    size: int = Query(10, description="Box size"),
    border: int = Query(4, description="Border size"),
    fg_color: str = Query("#000000", description="Foreground color as hex e.g. #ff0000"),
    bg_color: str = Query("#ffffff", description="Background color as hex e.g. #ffffff")
):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fg_color, back_color=bg_color)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
