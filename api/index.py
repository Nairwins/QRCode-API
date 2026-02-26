from fastapi import FastAPI, Query, File, UploadFile
from fastapi.responses import StreamingResponse
from typing import Optional
try:
    from api.engine import build_qr_image
    from api.assets import DEFAULT_SIZE, DEFAULT_BORDER, DEFAULT_GRADIENT, DEFAULT_SHAPE, DOT_SHAPES
except ImportError:
    from engine import build_qr_image
    from assets import DEFAULT_SIZE, DEFAULT_BORDER, DEFAULT_GRADIENT, DEFAULT_SHAPE, DOT_SHAPES

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "QR Code Generator API is running!",
        "available_shapes": DOT_SHAPES,
        "endpoint": "POST /generate"
    }

@app.post("/generate")
async def generate_qr(
    data: str = Query(..., description="Text or URL to encode"),
    logo: Optional[UploadFile] = File(None, description="Logo file (PNG, JPG, etc.) - optional"),
    size: int = Query(DEFAULT_SIZE, description="Box size"),
    border: int = Query(DEFAULT_BORDER, description="Border size"),
    fg_color: str = Query("black", description="Dot color — name or hex e.g. red / %23ff0000"),
    bg_color: str = Query("white", description="Background color — name or hex"),
    gradient_color: str = Query(None, description="Second gradient color — name or hex (optional)"),
    gradient_type: str = Query(DEFAULT_GRADIENT, description="horizontal | vertical | diagonal | diagonal_reverse | center | center_reverse"),
    eye_outer: str = Query(None, description="Outer eye color — name or hex (optional)"),
    eye_inner: str = Query(None, description="Inner eye color — name or hex (optional)"),
    dot_shape: str = Query(DEFAULT_SHAPE, description="square | circle | dot | rounded | smooth | diamond | diamond_small | star4 | star5 | cross | heart | triangle_up | triangle_down | hexagon | octagon | arrow_right | vertical_line | horizontal_line | x_shape | ring | bars"),
    logo_size: int = Query(25, description="Logo size as percentage of QR code (10-40)"),
):
    logo_bytes = None
    if logo:
        logo_bytes = await logo.read()
    
    buffer = build_qr_image(
        data=data,
        size=size,
        border=border,
        fg_color=fg_color,
        bg_color=bg_color,
        gradient_color=gradient_color,
        gradient_type=gradient_type,
        eye_outer=eye_outer,
        eye_inner=eye_inner,
        dot_shape=dot_shape,
        logo_bytes=logo_bytes,
        logo_size=logo_size,
    )
    return StreamingResponse(buffer, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)