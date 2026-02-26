import io
import cairosvg
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from api.engine import build_qr
from api.asset import ICONS, parse_color

app = FastAPI()

@app.post("/qr")
async def generate_qr(
    text: str = Query(..., description="Text to encode"),
    logo: UploadFile = File(None, description="Custom logo image"),
    default_icon: str = Query(None, description="Default icon name: 'gold', 'laser'"),
    body_color: str = Query("000000", description="Dot color — hex or name (e.g. 'red', '#ff0000', 'ff0000')"),
    bg_color: str = Query("ffffff", description="Background color"),
    outer_eye_color: str = Query(None, description="Outer eye frame color (defaults to body_color)"),
    inner_eye_color: str = Query(None, description="Inner eye dot color (defaults to body_color)"),
):
    logo_bytes = None

    if logo:
        logo_bytes = await logo.read()
    elif default_icon:
        icon_path = ICONS.get(default_icon)
        if not icon_path or not icon_path.exists():
            raise HTTPException(status_code=404, detail=f"Icon '{default_icon}' not found")
        logo_bytes = icon_path.read_bytes()

    body = parse_color(body_color)
    bg   = parse_color(bg_color, fallback="white")
    outer = parse_color(outer_eye_color) if outer_eye_color else body
    inner = parse_color(inner_eye_color) if inner_eye_color else body

    return Response(
        content=build_qr(text, logo_bytes, body, bg, outer, inner),
        media_type="image/png",
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)