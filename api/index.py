from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from api.engine import build_qr_image
from api.assets import DEFAULT_SIZE, DEFAULT_BORDER, DEFAULT_GRADIENT, DEFAULT_SHAPE, DOT_SHAPES, INNER_DIR, OUTER_DIR, list_svg_shapes

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "QR Code Generator API is running!",
        "dot_shapes": DOT_SHAPES,
        "eye_outer_shapes": list_svg_shapes(OUTER_DIR),
        "eye_inner_shapes": list_svg_shapes(INNER_DIR),
    }


@app.get("/generate")
def generate_qr(
    data: str = Query(..., description="Text or URL to encode"),
    size: int = Query(DEFAULT_SIZE, description="Box size"),
    border: int = Query(DEFAULT_BORDER, description="Border size"),
    fg_color: str = Query("black", description="Dot color — name or hex"),
    bg_color: str = Query("white", description="Background color — name or hex"),
    gradient_color: str = Query(None, description="Second gradient color — name or hex (optional)"),
    gradient_type: str = Query(DEFAULT_GRADIENT, description="horizontal | vertical | diagonal | diagonal_reverse | center | center_reverse"),
    eye_outer: str = Query(None, description="Outer eye color — name or hex (optional)"),
    eye_inner: str = Query(None, description="Inner eye color — name or hex (optional)"),
    dot_shape: str = Query(DEFAULT_SHAPE, description="Dot shape — see / for full list"),
    eye_outer_shape: str = Query(None, description="SVG name from outer/ folder e.g. eye"),
    eye_inner_shape: str = Query(None, description="SVG name from inner/ folder e.g. flower"),
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
        eye_outer_shape=eye_outer_shape,
        eye_inner_shape=eye_inner_shape,
    )

    return StreamingResponse(buffer, media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
