"""Tile pictures into one sheet with their file names (for looking at many at once)."""
import sys
from PIL import Image, ImageDraw
out, files = sys.argv[1], sys.argv[2:]
w, h = 640, 480
cols = 2
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * (h + 20)), "white")
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((w, h))
    x, y = (i % cols) * w, (i // cols) * (h + 20)
    sheet.paste(im, (x, y + 20))
    d.text((x + 5, y + 4), f.split("/")[-1], fill="black")
sheet.save(out)
