"""
Run from QRCode root:
    python3 script/mirror.py
"""
from PIL import Image
from pathlib import Path

to_rotate = [
    Path("api/outer/corner.png"),
]

for path in to_rotate:
    img = Image.open(path)
    img = img.rotate(90, expand=True)
    img.save(path)
    print(f"✅  rotated 90° {path}")