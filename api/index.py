from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, HTMLResponse
import base64
from pathlib import Path

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
    }

@app.get("/generate")
def generate_qr(
    data: str = Query(..., description="Text or URL to encode"),
    size: int = Query(DEFAULT_SIZE, description="Box size"),
    border: int = Query(DEFAULT_BORDER, description="Border size"),
    fg_color: str = Query("black", description="Dot color — name or hex e.g. red / %23ff0000"),
    bg_color: str = Query("white", description="Background color — name or hex"),
    gradient_color: str = Query(None, description="Second gradient color — name or hex (optional)"),
    gradient_type: str = Query(DEFAULT_GRADIENT, description="horizontal | vertical | diagonal | diagonal_reverse | center | center_reverse"),
    eye_outer: str = Query(None, description="Outer eye color — name or hex (optional)"),
    eye_inner: str = Query(None, description="Inner eye color — name or hex (optional)"),
    dot_shape: str = Query(DEFAULT_SHAPE, description="square | circle | dot | rounded | smooth | diamond | diamond_small | star4 | star5 | cross | heart | triangle_up | triangle_down | hexagon | octagon | arrow_right | vertical_line | horizontal_line | x_shape | ring | bars"),
    inner_eye_shape: str = Query(None, description="Inner eye SVG shape (e.g., 'flower')"),
    outer_eye_shape: str = Query(None, description="Outer eye SVG shape (e.g., 'eye')"),
):
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
    )
    
    # If no SVG shapes requested, return just the QR code
    if not inner_eye_shape and not outer_eye_shape:
        return StreamingResponse(buffer, media_type="image/png")
    
    # Convert QR code to base64
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    html = "<div style='display:flex; gap:20px;'>"
    html += f"<img src='data:image/png;base64,{qr_base64}' style='width:300px;'>"
    
    # Debug info
    debug_info = []
    
    # Add inner eye SVG if requested
    if inner_eye_shape:
        svg_path = Path(__file__).parent / "api/inner" / f"{inner_eye_shape}.svg"
        debug_info.append(f"Looking for inner: {svg_path}")
        if svg_path.exists():
            svg_content = svg_path.read_text()
            html += f"<div style='width:300px;'>{svg_content}</div>"
            debug_info.append("Inner SVG found!")
        else:
            debug_info.append(f"Inner SVG NOT found at: {svg_path}")
    
    # Add outer eye SVG if requested  
    if outer_eye_shape:
        svg_path = Path(__file__).parent / "api/outer" / f"{outer_eye_shape}.svg"
        debug_info.append(f"Looking for outer: {svg_path}")
        if svg_path.exists():
            svg_content = svg_path.read_text()
            html += f"<div style='width:300px;'>{svg_content}</div>"
            debug_info.append("Outer SVG found!")
        else:
            debug_info.append(f"Outer SVG NOT found at: {svg_path}")
    
    html += "</div>"
    
    # Add debug info
    html += "<div style='margin-top:20px; padding:10px; background:#f0f0f0;'>"
    html += "<h3>Debug Info:</h3>"
    for info in debug_info:
        html += f"<p>{info}</p>"
    html += "</div>"
    
    return HTMLResponse(content=html)

# Export for Vercel
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)