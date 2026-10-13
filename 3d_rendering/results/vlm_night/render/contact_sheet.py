"""Contact sheet of pictures, for checking by eye.
    python contact_sheet.py OUT.jpg PIC1.jpg PIC2.jpg ...   (labels are the file names)"""
import pathlib
import sys

from PIL import Image, ImageDraw

out, files = sys.argv[1], sys.argv[2:]
tw, th, cols = 320, 240, 4
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 14)), "white")
d = ImageDraw.Draw(sheet)
for n, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((tw, th))
    x, y = (n % cols) * tw, (n // cols) * (th + 14)
    sheet.paste(im, (x, y + 14))
    d.text((x + 2, y + 1), f"{n}: " + pathlib.Path(f).stem[:52], fill="black")
sheet.save(out, quality=85)
