from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw
import qrcode
from io import BytesIO

app = FastAPI()


def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient(width, height, color1, color2, gradient_type):
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)

    gradient = Image.new("RGB", (width, height))
    pixels = gradient.load()

    for y in range(height):
        for x in range(width):
            if gradient_type == "horizontal":
                t = x / (width - 1)
            elif gradient_type == "vertical":
                t = y / (height - 1)
            elif gradient_type == "diagonal":
                t = (x + y) / (width + height - 2)
            elif gradient_type == "diagonal_reverse":
                t = (x + (height - y)) / (width + height - 2)
            elif gradient_type == "center":
                cx, cy = width / 2, height / 2
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                max_dist = (cx ** 2 + cy ** 2) ** 0.5
                t = dist / max_dist
            elif gradient_type == "center_reverse":
                cx, cy = width / 2, height / 2
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                max_dist = (cx ** 2 + cy ** 2) ** 0.5
                t = 1 - (dist / max_dist)
            else:
                t = x / (width - 1)

            t = max(0.0, min(1.0, t))
            pixels[x, y] = (
                int(r1 + (r2 - r1) * t),
                int(g1 + (g2 - g1) * t),
                int(b1 + (b2 - b1) * t),
            )

    return gradient


def draw_eyes(img, box_size, border, modules_count, outer_color, inner_color, bg_color):
    draw = ImageDraw.Draw(img)

    eye_positions = [
        (0, 0),                        # top-left
        (0, modules_count - 7),        # top-right
        (modules_count - 7, 0),        # bottom-left
    ]

    for (row, col) in eye_positions:
        x = (col + border) * box_size
        y = (row + border) * box_size

        # Outer 7x7 square
        draw.rectangle([x, y, x + 7 * box_size - 1, y + 7 * box_size - 1], fill=outer_color)
        # Background gap (5x5)
        draw.rectangle([x + box_size, y + box_size, x + 6 * box_size - 1, y + 6 * box_size - 1], fill=bg_color)
        # Inner dot (3x3)
        draw.rectangle([x + 2 * box_size, y + 2 * box_size, x + 5 * box_size - 1, y + 5 * box_size - 1], fill=inner_color)


@app.get("/")
def root():
    return {"message": "QR Code Generator API is running!"}


@app.get("/generate")
def generate_qr(
    data: str = Query(..., description="Text or URL to encode"),
    size: int = Query(10, description="Box size"),
    border: int = Query(4, description="Border size"),
    fg_color: str = Query("#000000", description="Main dot color"),
    bg_color: str = Query("#ffffff", description="Background color"),
    gradient_color: str = Query(None, description="Second gradient color (optional)"),
    gradient_type: str = Query("horizontal", description="horizontal | vertical | diagonal | diagonal_reverse | center | center_reverse"),
    eye_outer: str = Query(None, description="Outer eye color (defaults to fg_color)"),
    eye_inner: str = Query(None, description="Inner eye color (defaults to fg_color)"),
):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    modules_count = qr.modules_count

    if gradient_color:
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        width, height = qr_img.size

        result = Image.new("RGB", (width, height), hex_to_rgb(bg_color))
        gradient = create_gradient(width, height, fg_color, gradient_color, gradient_type)

        mask = qr_img.convert("L").point(lambda p: 255 if p < 128 else 0)
        result.paste(gradient, (0, 0), mask)
        final_img = result
    else:
        final_img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGB")

    # Draw custom eye colors
    outer_color = hex_to_rgb(eye_outer) if eye_outer else hex_to_rgb(fg_color)
    inner_color = hex_to_rgb(eye_inner) if eye_inner else hex_to_rgb(fg_color)
    bg_rgb = hex_to_rgb(bg_color)

    draw_eyes(final_img, size, border, modules_count, outer_color, inner_color, bg_rgb)

    buffer = BytesIO()
    final_img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
