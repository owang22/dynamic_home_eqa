"""Printable ArUco markers (DICT_4X4_50) for the Go2 line-up marks: one per US-letter page at 300 dpi,
black square exactly SIZE_CM wide. Writes markers.pdf plus one PNG per marker, and checks each is detectable."""
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
DPI, SIZE_CM = 300, 18.0
MARKS = [("A", 0), ("B", 1), ("C", 2), ("D", 3), ("spare", 4), ("spare", 5)]
W, H = int(8.5 * DPI), int(11 * DPI)
px = int(round(SIZE_CM / 2.54 * DPI))
d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
det = cv2.aruco.ArucoDetector(d, cv2.aruco.DetectorParameters())
try:
    big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 260)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
except OSError:
    big = small = ImageFont.load_default()
pages = []
for name, mid in MARKS:
    m = cv2.aruco.generateImageMarker(d, mid, px)
    page = Image.new("L", (W, H), 255)
    x0, y0 = (W - px) // 2, int(1.0 * DPI)
    page.paste(Image.fromarray(m), (x0, y0))
    dr = ImageDraw.Draw(page)
    title = name if name != "spare" else f"spare {mid}"
    dr.text((W // 2, y0 + px + 60), title, font=big, fill=0, anchor="ma")
    dr.text((W // 2, H - int(0.9 * DPI)), f"Go2 mark {title} · ArUco 4x4_50 id {mid} · black square {SIZE_CM:.1f} cm wide — print at 100%, no scaling",
            font=small, fill=0, anchor="ma")
    arr = np.array(page)
    found = det.detectMarkers(arr)[1]
    assert found is not None and int(found[0][0]) == mid, (name, mid, found)
    page.save(f"/w/mark_{title.replace(' ', '_')}_id{mid}.png", dpi=(DPI, DPI))
    pages.append(page.convert("RGB"))
pages[0].save("/w/markers.pdf", save_all=True, append_images=pages[1:], resolution=DPI)
print("ok", len(pages), "pages; square", px, "px =", SIZE_CM, "cm")
