
import cairosvg
from pathlib import Path

folders = [Path("api/inner"), Path("api/outer")]

for folder in folders:
    for svg in folder.glob("*.svg"):
        out = svg.with_suffix(".png")
        cairosvg.svg2png(url=str(svg), write_to=str(out), output_width=500, output_height=500)
        print(f"✅  {svg} → {out}")

print("\nDone! All SVGs converted.")