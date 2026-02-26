import io
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from api.engine import build_qr
from api.asset import ICONS, INNER_EYES, OUTER_EYES, DOT_STYLES, parse_color

app = FastAPI()

@app.post("/qr")
async def generate_qr(
    text: str = Query(..., description="Text to encode"),

    # Logo
    logo: UploadFile = File(None, description="Custom logo image"),
    default_icon: str = Query(None, description="facebook | gmail | gold | instagram | linkedin | paypal | phone | pinterest | snapchat | spotify | telegram | twitch | twitter | whatsapp | wifi | youtube"),

    # Colors
    body_color:      str = Query("000000"),
    bg_color:        str = Query("ffffff"),
    outer_eye_color: str = Query(None, description="Defaults to body_color"),
    inner_eye_color: str = Query(None, description="Defaults to body_color"),

    # Gradient
    gradient_color: str = Query(None),
    gradient_type:  str = Query(None, description="horizontal | vertical | diagonal | center"),

    # Dot style
    dot_style: str = Query("square", description="square | dot | block | rounded | diamond | smooth | vertical | horizontal | aura"),

    # Logo size
    icon_size: float = Query(0.25, ge=0.10, le=0.40, description="Logo size as fraction of QR width (0.10–0.40)"),

    # Eye shapes
    outer_eye_shape: str = Query(None, description="bloop | circle | corner | eye | floop | octagon | rounded | rounder | target | zig"),
    inner_eye_shape: str = Query(None, description="clog | cloud | diamond | flower | heart | petal | rounded | sphere | star | target | x"),
):
    # Logo
    logo_bytes = None
    if logo:
        logo_bytes = await logo.read()
    elif default_icon:
        icon_path = ICONS.get(default_icon)
        if not icon_path or not icon_path.exists():
            raise HTTPException(status_code=404, detail=f"Icon '{default_icon}' not found")
        logo_bytes = icon_path.read_bytes()

    # Eye PNGs
    outer_png = None
    if outer_eye_shape:
        outer_png = OUTER_EYES.get(outer_eye_shape)
        if not outer_png or not outer_png.exists():
            raise HTTPException(status_code=404, detail=f"Outer eye '{outer_eye_shape}' not found")

    inner_png = None
    if inner_eye_shape:
        inner_png = INNER_EYES.get(inner_eye_shape)
        if not inner_png or not inner_png.exists():
            raise HTTPException(status_code=404, detail=f"Inner eye '{inner_eye_shape}' not found")

    # Validate
    if dot_style not in DOT_STYLES:
        raise HTTPException(status_code=422, detail=f"dot_style must be one of: {DOT_STYLES}")

    valid_gradients = {"horizontal", "vertical", "diagonal", "center"}
    if gradient_type and gradient_type not in valid_gradients:
        raise HTTPException(status_code=422, detail=f"gradient_type must be one of: {valid_gradients}")

    # Parse colors
    body  = parse_color(body_color)
    bg    = parse_color(bg_color, fallback="white")
    outer = parse_color(outer_eye_color) if outer_eye_color else body
    inner = parse_color(inner_eye_color) if inner_eye_color else body
    grad  = parse_color(gradient_color)  if gradient_color  else None

    return Response(
        content=build_qr(
            text, logo_bytes,
            body, bg, outer, inner,
            outer_png, inner_png,
            grad, gradient_type,
            dot_style,
            logo_size_ratio=icon_size,
        ),
        media_type="image/png",
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)