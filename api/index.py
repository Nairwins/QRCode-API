from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from mangum import Mangum
import qrcode
import io

app = FastAPI()

@app.get("/api/qr")
def generate_qr(data: str = Query(...)):
    qr = qrcode.make(data)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

handler = Mangum(app)