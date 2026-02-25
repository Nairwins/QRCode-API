from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from engine import build_qr_image
from assets import DEFAULT_SIZE, DEFAULT_BORDER, DEFAULT_GRADIENT

app = FastAPI()


@app.get("/")
def root():
    return {"message": "QR Code Generator API is running!"}


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
    )

    return StreamingResponse(buffer, media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)