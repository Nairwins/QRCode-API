import io
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from api.engine import build_qr
from api.asset import ICONS, INNER_EYES, OUTER_EYES, parse_color

app = FastAPI()

@app.post("/qr")
async def generate_qr(
    text: str = Query(..., description="Text to encode"),

    # Logo
    logo: UploadFile = File(None, description="Custom logo image"),
    default_icon: str = Query(None, description="Default icon name: 'gold', 'laser'"),

    # Colors
    body_color:      str = Query("000000", description="Dot color"),
    bg_color:        str = Query("ffffff", description="Background color"),
    outer_eye_color: str = Query(None,     description="Outer eye color (defaults to body_color)"),
    inner_eye_color: str = Query(None,     description="Inner eye color (defaults to body_color)"),

    # Eye shapes
    outer_eye_shape: str = Query(None, description="Outer eye shape name e.g. 'eye'"),
    inner_eye_shape: str = Query(None, description="Inner eye shape name e.g. 'flower'"),
):
    # Resolve logo
    logo_bytes = None
    if logo:
        logo_bytes = await logo.read()
    elif default_icon:
        icon_path = ICONS.get(default_icon)
        if not icon_path or not icon_path.exists():
            raise HTTPException(status_code=404, detail=f"Icon '{default_icon}' not found")
        logo_bytes = icon_path.read_bytes()

    # Resolve eye PNGs
    outer_png = None
    if outer_eye_shape:
        outer_png = OUTER_EYES.get(outer_eye_shape)
        if not outer_png or not outer_png.exists():
            raise HTTPException(status_code=404, detail=f"Outer eye shape '{outer_eye_shape}' not found")

    inner_png = None
    if inner_eye_shape:
        inner_png = INNER_EYES.get(inner_eye_shape)
        if not inner_png or not inner_png.exists():
            raise HTTPException(status_code=404, detail=f"Inner eye shape '{inner_eye_shape}' not found")

    # Parse colors
    body  = parse_color(body_color)
    bg    = parse_color(bg_color, fallback="white")
    outer = parse_color(outer_eye_color) if outer_eye_color else body
    inner = parse_color(inner_eye_color) if inner_eye_color else body

    return Response(
        content=build_qr(text, logo_bytes, body, bg, outer, inner, outer_png, inner_png),
        media_type="image/png",
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)