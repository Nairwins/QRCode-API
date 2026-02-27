import io
import base64
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from api.engine import build_qr
from api.asset import ICONS, INNER_EYES, OUTER_EYES, DOT_STYLES, parse_color

app = FastAPI()


def _build(
    text, logo_bytes, body_color, bg_color,
    outer_eye_color, inner_eye_color,
    gradient_color, gradient_type,
    dot_style, icon_size,
    outer_eye_shape, inner_eye_shape,
):
    """Shared validation + build logic for both GET and POST."""
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

    if dot_style not in DOT_STYLES:
        raise HTTPException(status_code=422, detail=f"dot_style must be one of: {DOT_STYLES}")

    valid_gradients = {"horizontal", "vertical", "diagonal", "center"}
    if gradient_type and gradient_type not in valid_gradients:
        raise HTTPException(status_code=422, detail=f"gradient_type must be one of: {valid_gradients}")

    body  = parse_color(body_color)
    bg    = parse_color(bg_color, fallback="white")
    outer = parse_color(outer_eye_color) if outer_eye_color else body
    inner = parse_color(inner_eye_color) if inner_eye_color else body
    grad  = parse_color(gradient_color)  if gradient_color  else None

    return build_qr(
        text, logo_bytes,
        body, bg, outer, inner,
        outer_png, inner_png,
        grad, gradient_type,
        dot_style,
        logo_size_ratio=icon_size,
    )


def _respond(png_bytes, fmt, filename, download):
    """Build the final response with correct headers."""
    if fmt == "svg":
        b64 = base64.b64encode(png_bytes).decode()
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 500 500" width="500" height="500">
  <image href="data:image/png;base64,{b64}" width="500" height="500"/>
</svg>'''
        return Response(
            content=svg.encode(),
            media_type="image/svg+xml",
            headers={
                "Content-Disposition": f"{'attachment' if download else 'inline'}; filename=\"{filename}.svg\"",
                "Cache-Control": "no-cache",
            }
        )

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f"{'attachment' if download else 'inline'}; filename=\"{filename}.png\"",
            "Cache-Control": "no-cache",
        }
    )


# ── POST — supports custom logo upload ───────────────────────────────────────

@app.post("/qr")
async def generate_qr_post(
    text: str = Query(...),
    logo: UploadFile = File(None, description="Custom logo image"),
    default_icon: str = Query(None, description="facebook | gmail | gold | instagram | linkedin | paypal | phone | pinterest | snapchat | spotify | telegram | twitch | twitter | whatsapp | wifi | youtube"),
    body_color:      str   = Query("000000"),
    bg_color:        str   = Query("ffffff"),
    outer_eye_color: str   = Query(None),
    inner_eye_color: str   = Query(None),
    gradient_color:  str   = Query(None),
    gradient_type:   str   = Query(None, description="horizontal | vertical | diagonal | center"),
    dot_style:       str   = Query("square", description="square | dot | block | rounded | diamond | smooth | vertical | horizontal | aura"),
    fmt:             str   = Query("png", description="png | svg"),
    filename:        str   = Query("qrcode"),
    download:        bool  = Query(False),
    icon_size:       float = Query(0.25, ge=0.10, le=0.40),
    outer_eye_shape: str   = Query(None, description="bloop | circle | corner | eye | floop | octagon | rounded | rounder | target | zig"),
    inner_eye_shape: str   = Query(None, description="clog | cloud | diamond | flower | heart | petal | rounded | sphere | star | target | x"),
):
    logo_bytes = None
    if logo:
        logo_bytes = await logo.read()
    elif default_icon:
        icon_path = ICONS.get(default_icon)
        if not icon_path or not icon_path.exists():
            raise HTTPException(status_code=404, detail=f"Icon '{default_icon}' not found")
        logo_bytes = icon_path.read_bytes()

    png_bytes = _build(text, logo_bytes, body_color, bg_color,
                       outer_eye_color, inner_eye_color,
                       gradient_color, gradient_type,
                       dot_style, icon_size,
                       outer_eye_shape, inner_eye_shape)

    return _respond(png_bytes, fmt, filename, download)


# ── GET — browser-friendly, auto-download via URL ────────────────────────────

@app.get("/qr")
def generate_qr_get(
    text: str = Query(...),
    default_icon: str   = Query(None, description="facebook | gmail | gold | instagram | linkedin | paypal | phone | pinterest | snapchat | spotify | telegram | twitch | twitter | whatsapp | wifi | youtube"),
    body_color:      str   = Query("000000"),
    bg_color:        str   = Query("ffffff"),
    outer_eye_color: str   = Query(None),
    inner_eye_color: str   = Query(None),
    gradient_color:  str   = Query(None),
    gradient_type:   str   = Query(None, description="horizontal | vertical | diagonal | center"),
    dot_style:       str   = Query("square", description="square | dot | block | rounded | diamond | smooth | vertical | horizontal | aura"),
    fmt:             str   = Query("png", description="png | svg"),
    filename:        str   = Query("qrcode"),
    download:        bool  = Query(False),
    icon_size:       float = Query(0.25, ge=0.10, le=0.40),
    outer_eye_shape: str   = Query(None, description="bloop | circle | corner | eye | floop | octagon | rounded | rounder | target | zig"),
    inner_eye_shape: str   = Query(None, description="clog | cloud | diamond | flower | heart | petal | rounded | sphere | star | target | x"),
):
    logo_bytes = None
    if default_icon:
        icon_path = ICONS.get(default_icon)
        if not icon_path or not icon_path.exists():
            raise HTTPException(status_code=404, detail=f"Icon '{default_icon}' not found")
        logo_bytes = icon_path.read_bytes()

    png_bytes = _build(text, logo_bytes, body_color, bg_color,
                       outer_eye_color, inner_eye_color,
                       gradient_color, gradient_type,
                       dot_style, icon_size,
                       outer_eye_shape, inner_eye_shape)

    return _respond(png_bytes, fmt, filename, download)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)